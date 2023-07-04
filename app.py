from flask import Flask, render_template, request
from arvoreb import BTree
from random import randint

app = Flask(__name__)
app = Flask(__name__, static_folder='static')

@app.template_global()
def is_list(obj):
    return isinstance(obj, list)

@app.route('/', methods=['GET', 'POST'])
def index():
    opcao_escolhida = 3

    if request.method == 'POST':
        opcao_escolhida = request.form.get('grau')
        # Faça algo com a opção escolhida
    if opcao_escolhida is None:
        opcao_escolhida = 3

    arvore = BTree(int(opcao_escolhida))

    n = 10  # número de valores aleatorios a ser gerado
    valores_aleatorios = []
    for i in range(0, n):
        aleatorio = randint(0, 200) # valores entre 0 e 200
        arvore.add(aleatorio) # valor adicionado na arvore
        valores_aleatorios.append(aleatorio) # lista de ordem em que os valores foram adicionados

    valores_aleatorios = ''.join(str(valores_aleatorios))

    raiz = str(arvore.root.values)
    filhos = []

    for filho in arvore.root.children:
        if isinstance(filho, list):
            filhos.append(filho)
        else:
            filhos.append(str(filho))

    return render_template('index.html', aleatorio=valores_aleatorios, raiz=raiz, filhos=filhos)


if __name__ == '__main__':
    app.run(debug=True)
