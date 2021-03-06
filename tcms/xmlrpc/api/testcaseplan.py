# -*- coding: utf-8 -*-

from modernrpc.core import rpc_method

from tcms.testcases.models import TestCasePlan
from tcms.xmlrpc.serializer import XMLRPCSerializer

__all__ = ('get', 'update')


@rpc_method(name='TestCasePlan.get')
def get(case_id, plan_id):
    """
    Description: Used to load an existing test-case-plan from the database.

    Params:      $case_id - Integer: An integer representing the ID of the test case
                                     in the database.
                 $plan_id - Integer: An integer representing the ID of the test plan
                                     in the database.

    Returns:     A blessed TestCasePlan object hash

    Example:
    >>> TestCasePlan.get(81307, 3551)
    """
    if not isinstance(case_id, int):
        raise ValueError('Parameter case_id must be an integer')

    if not isinstance(plan_id, int):
        raise ValueError('Parameter plan_id must be an integer')

    tcp = TestCasePlan.objects.get(plan_id=plan_id, case_id=case_id)
    return XMLRPCSerializer(model=tcp).serialize_model()


@rpc_method(name='TestCasePlan.update')
def update(case_id, plan_id, sortkey):
    """
    Description: Updates the sortkey of the selected test-case-plan.

    Params:      $case_id - Integer: An integer representing the ID of the test case
                                     in the database.
                 $plan_id - Integer: An integer representing the ID of the test plan
                                     in the database.
                 $sortkey - Integer: An integer representing the ID of the sortkey
                                     in the database.

    Returns:     A blessed TestCasePlan object hash

    Example:
    # Update sortkey of selected test-case-plan to 450
    >>> TestCasePlan.update(81307, 3551, 450)
    """

    if not isinstance(case_id, int):
        raise ValueError('Parameter case_id must be an integer')

    if not isinstance(plan_id, int):
        raise ValueError('Parameter plan_id must be an integer')

    tcp = TestCasePlan.objects.get(plan_id=plan_id, case_id=case_id)

    if isinstance(sortkey, int):
        tcp.sortkey = sortkey
        tcp.save(update_fields=['sortkey'])

    return XMLRPCSerializer(model=tcp).serialize_model()
