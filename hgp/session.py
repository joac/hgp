### Implement filesystem session store
from flask import Flask,
from werkzeug.contrib.sessions import FilesystemSessionStore

session_store = FilesystemSessionStore()


class SessionMixin(object):
    session_key = 'f2949161db8940bba770501b9b486b71'

    def open_session(self, request):
        sid = request.cookies.get(self.session_key, None) or \
                request.values.get(self.session_key, None)
        if sid is None:
            return session_store.new()
        else:
            return session_store.get(sid)

    def save_session(self, session, response):
        if session.should_save:
            session_store.save(session)
            response.set_cookie(self.session_key, session.sid)
        return response


class FlaskSess(SessionMixin, Flask):
    pass
