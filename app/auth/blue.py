from . import auth_bp

@auth_bp.route("/blue")
def print_blue():
	return "hello Blue!"