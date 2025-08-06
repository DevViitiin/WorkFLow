import os

def corrigir_long_em_buildozer():
    raiz = ".buildozer/android/platform/build"
    for dirpath, _, filenames in os.walk(raiz):
        for filename in filenames:
            if filename.endswith('.py'):
                caminho = os.path.join(dirpath, filename)
                try:
                    with open(caminho, 'r', encoding='utf-8') as f:
                        conteudo = f.read()
                    if 'long(' in conteudo:
                        conteudo_corrigido = conteudo.replace('long(', 'int(')
                        with open(caminho, 'w', encoding='utf-8') as f:
                            f.write(conteudo_corrigido)
                        print(f'✔ Corrigido: {caminho}')
                except Exception as e:
                    print(f'⚠️ Erro ao ler {caminho}: {e}')

if __name__ == "__main__":
    corrigir_long_em_buildozer()
