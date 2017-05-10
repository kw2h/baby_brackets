from flask_admin.contrib.sqla import ModelView
from flask import g

class AdminModelView(ModelView):
    def is_accessible(self):
        """Return True if user is logged in and an administrator"""
        return g.user is not None and g.user.is_authenticated and g.user.role_id == '0'

    def inaccessible_callback(self, name, **kwargs):
        """Redirect to login page if user doesn't have access"""
        return redirect(url_for('login', next=request.url))
