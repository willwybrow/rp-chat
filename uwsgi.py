from chat.web import app as application
from chat.web import config

if __name__ == "__main__":
    import ssl

    context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
    context.load_cert_chain(config['secrets']['testing_ssl_cert'], config['secrets']['testing_ssl_key'])
    application.run(debug=True, host='0.0.0.0', port=config['app']['port'], ssl_context=context)
