from flask import Flask, render_template, jsonify, request, session, redirect
from models import db, connect_db, User, Feedback
from flask_debugtoolbar import DebugToolbarExtension
from forms import CreateUserForm, LoginForm, FeedbackForm
from werkzeug.exceptions import Unauthorized


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///auths'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = '12345'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

app.debug = True
debug = DebugToolbarExtension(app)

app_context = app.app_context()
app_context.push()

connect_db(app)
db.drop_all()
db.create_all()

@app.route('/')
def redirect_register():
    """Redirects user to /register."""
    return redirect('/register')

@app.route('/register', methods=['GET', 'POST'])
def show_registration_form():
    """Show registration form and handle registration."""
    form = CreateUserForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        
        user = User.register(username=username, password=password, email=email, first_name=first_name, last_name=last_name)
        
        db.session.add(user)
        db.session.commit()

        session['username'] = user.username
        
        return redirect(f'/users/{user.username}')
    else:
        return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def show_login():
    """Show login form and handle login."""
    
    if "username" in session:
        return redirect(f"/users/{session['username']}")

    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.username.data

        user = User.authenticate(username, password)

        if user:
            session['username'] = user.username
            return redirect(f'/users/{user.username}')
        else:
            form.username.errors = ["Invalid username/password"]
            return render_template("users/login.html", form=form)
    
    return render_template('login.html', form=form)
    
@app.route('/users/<username>')
def show_secret(username):
    """Show information about given user and all the feedback user has given."""
    form = FeedbackForm()

    if "username" not in session or username != session['username']:
        raise Unauthorized()

    user = User.query.get_or_404(username)

    return render_template('user.html', user=user, form=form)
    
@app.route('/logout')
def logout():
    """Logout user."""

    session.pop('username')
    return redirect('/')

@app.route('/users/<username>/delete', methods=['POST'])
def delete_user(username):
    """Delete user and all user feedback."""

    if "username" not in session or username != session["username"]:
        raise Unauthorized()
    
    user = User.query.get_or_404(username)

    db.session.delete(user)
    db.session.commit()

    session.pop('username')

    return redirect('/')

@app.route('/users/<username>/feedback/add', methods=['GET', 'POST'])
def add_feedback(username):
    """Show form for adding user feedback and handle form submission."""

    if "username" not in session or username !=session["username"]:
        raise Unauthorized()

    form = FeedbackForm()

    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data

        feedback = Feedback(
            title=title,
            content=content,
            username=username
        )
        
        db.session.add(feedback)
        db.session.commit()

        return redirect(f'/users/{username}')
    else:
        return render_template('add_feedback.html', form=form)

@app.route('/feedback/<int:feedback_id>/update', methods=['GET', 'POST'])
def update_feedback(feedback_id):
    """Show form for updating feedback and handle form submission."""

    feedback = Feedback.query.get_or_404(feedback_id)

    if "username" not in session or feedback.username != session["username"]:
        raise Unauthorized()
    
    form = FeedbackForm(obj=feedback)
    
    if form.validate_on_submit():
        feedback.title = form.title.data
        feedback.content = form.content.data

        db.session.commit()

        return redirect(f'/users/{feedback.username}')

    return render_template('edit_feedback.html', form=form, feedback=feedback)

@app.route('/feedback/<int:feedback_id>/delete', methods=['POST'])
def delete_feedback(feedback_id):
    """Delete feedback from db."""

    feedback = Feedback.query.get_or_404(feedback_id)

    if "username" not in session or feedback.username != session["username"]:
        raise Unauthorized()
    
    db.session.delete(feedback)
    db.session.commit()

    return redirect(f'/users/{feedback.username}')