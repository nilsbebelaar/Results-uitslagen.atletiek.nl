from app import init_app
from werkzeug.middleware.proxy_fix import ProxyFix

app = init_app()
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_host=1) 

if __name__ == "__main__":
    app.run(host='0.0.0.0')
