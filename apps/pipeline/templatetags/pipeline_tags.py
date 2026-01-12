from django import template
from apps.pipeline.models import Deal

register = template.Library()

# Mapping of stage values to their info
STAGE_INFO = {
    'NEW_REQUEST': {'label': 'New Request', 'index': 0},
    'ENGAGED': {'label': 'Engaged', 'index': 1},
    'ESTIMATE_IN_PROGRESS': {'label': 'Estimate In Progress', 'index': 2},
    'ESTIMATE_SENT': {'label': 'Estimate Sent', 'index': 3},
    'FOLLOW_UP': {'label': 'Follow Up', 'index': 4},
    'NEGOTIATION': {'label': 'Negotiation', 'index': 5},
    'CLOSED_WON': {'label': 'Closed Won', 'index': 6},
    'CLOSED_LOST': {'label': 'Closed Lost', 'index': 7},
    'DECLINED_TO_BID': {'label': 'Declined to Bid', 'index': 8},
}


@register.filter
def get_stage_info(stage_value):
    """Get stage info dict from stage value."""
    return STAGE_INFO.get(stage_value, {'label': stage_value, 'index': -1})


@register.filter
def stage_index(stage_value):
    """Get the index of a stage for comparison."""
    info = STAGE_INFO.get(stage_value)
    return info['index'] if info else -1


@register.filter
def stage_label(stage_value):
    """Get the display label for a stage."""
    info = STAGE_INFO.get(stage_value)
    return info['label'] if info else stage_value


@register.simple_tag
def get_all_stages():
    """Return all stages in order."""
    return Deal.get_stage_order()


@register.simple_tag
def get_active_stages():
    """Return active pipeline stages."""
    return Deal.ACTIVE_STAGES


@register.simple_tag
def get_closed_stages():
    """Return closed stages."""
    return Deal.CLOSED_STAGES


@register.filter
def split(value, delimiter=','):
    """Split a string by delimiter."""
    return value.split(delimiter)
