from webapp import create_app
import os

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, port = port)
    #Comentar arriba para hacer un .exe con waitress
    #Descomentar abajo para hacer un .exe con waitress
    #from waitress import serve
    #serve(app, host="127.0.0.1", port=port)