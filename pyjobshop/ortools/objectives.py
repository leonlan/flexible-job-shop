from ortools.sat.python.cp_model import CpModel, LinearExpr

from pyjobshop.ProblemData import ProblemData

from .variables import JobVar, OperationVar


def makespan(model: CpModel, data: ProblemData, op_vars: list[OperationVar]):
    """
    Minimizes the makespan.
    """
    makespan = model.new_int_var(0, data.planning_horizon, "makespan")
    completion_times = [var.end for var in op_vars]

    model.add_max_equality(makespan, completion_times)
    model.minimize(makespan)


def tardy_jobs(m: CpModel, data: ProblemData, job_vars: list[JobVar]):
    """
    Minimize the number of tardy jobs.
    """
    exprs = []

    for job, job_var in zip(data.jobs, job_vars):
        is_tardy = m.new_bool_var(f"is_tardy_{job}")
        exprs.append(is_tardy)

        m.add(job_var.end > job.due_date).only_enforce_if(is_tardy)
        m.add(job_var.end <= job.due_date).only_enforce_if(~is_tardy)

    m.minimize(LinearExpr.sum(exprs))


def total_completion_time(
    m: CpModel, data: ProblemData, job_vars: list[JobVar]
):
    """
    Minimizes the weighted sum of the completion times of each job.
    """
    exprs = [job_var.end for job_var in job_vars]
    weights = [job_data.weight for job_data in data.jobs]

    m.minimize(LinearExpr.weighted_sum(exprs, weights))


def total_tardiness(m: CpModel, data: ProblemData, job_vars: list[JobVar]):
    """
    Minimizes the weighted sum of the tardiness of each job.
    """
    exprs = []

    for job, job_var in zip(data.jobs, job_vars):
        tardiness = m.new_int_var(0, data.planning_horizon, f"tardiness_{job}")
        exprs.append(tardiness)

        m.add_max_equality(tardiness, [0, job_var.end - job.due_date])

    weights = [job.weight for job in data.jobs]
    m.minimize(LinearExpr.weighted_sum(exprs, weights))
