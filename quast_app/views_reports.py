import os
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseBadRequest, Http404, HttpResponseRedirect
from django.conf import settings
from django.shortcuts import render_to_response

from views_report import task_state_map
from tasks import start_quast
from models import UserSession, DataSet, QuastSession

import logging
logger = logging.getLogger('quast')
mailer = logging.getLogger('quast_mailer')



def get_reports_response_dict(user_session, after_evaluation=False, limit=None):
    quast_sessions_dict = []

    quast_sessions = user_session.get_quastsession_set().filter(submitted=True).order_by('-date')
    if limit:
        quast_sessions = quast_sessions[:limit+1]

    show_more_link = False

    if quast_sessions.exists():
        # quast_sessions.sort(cmp=lambda qs1, qs2: 1 if qs1.date < qs2.date else -1)

        # if after_evaluation:
        #     last = quast_sessions[0]
        #     result = tasks.start_quast.AsyncResult(last.task_id)
        #     if result and result.state == 'SUCCESS':
        #         return redirect('/report/', report_id=last.report_id)

        for i, qs in enumerate(quast_sessions):
            if i == limit:
                show_more_link = True

            else:
                result = start_quast.AsyncResult(qs.task_id)
                state = result.state
                state_repr = 'FAILURE'
                if result and state in task_state_map:
                    state_repr = task_state_map[state]

                quast_session_info = {
                    'date': qs.date, #. strftime('%d %b %Y %H:%M:%S'),
                    'report_link': settings.REPORT_LINK_BASE + (qs.link or qs.report_id),
                    'comment' : qs.comment,
                    'caption' : qs.caption,
                    'with_data_set': True if qs.data_set else False,
                    'data_set_name': qs.data_set.name if qs.data_set and qs.data_set.remember else '',
                    'state': state_repr,
                    'report_id': qs.report_id,
                    'contigs': [cf.fname for cf in qs.contigs_files.all()],
                    }
                quast_sessions_dict.append(quast_session_info)

    return {
        'quast_sessions': quast_sessions_dict,
        'show_more_link': show_more_link,
        'highlight_last': after_evaluation,
        'latest_report_link': quast_sessions_dict[0]['report_link'] if after_evaluation else None
    }


def reports_view(user_session, response_dict, request, after_evaluation=False):
    response_dict = dict(response_dict.items() +
                         get_reports_response_dict(
                             user_session,
                             after_evaluation
                         ).items())

    return render_to_response('reports.html', response_dict)




