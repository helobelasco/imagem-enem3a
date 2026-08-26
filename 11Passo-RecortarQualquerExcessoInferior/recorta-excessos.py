from PIL import Image
import os
import shutil

def encontrar_faixa_inferior(imagem, cor_alvo=(35, 31, 32), tolerancia=15):
    """
    Procura de baixo para cima (da metade inferior da imagem) por um padrão visual 
    de 25 pixels de largura por 4 pixels de altura (aceitando de 2 a 6 px de altura).
    Retorna a posição Y acima do padrão para realizar o corte.
    """
    largura, altura = imagem.size
    pixels = imagem.load()
    
    # Define o centro horizontal para procurar os 25 pixels de largura (12 para a esquerda, 12 para a direita)
    x_centro = largura // 2
    x_inicio = x_centro - 12
    x_fim = x_centro + 12
    
    # Margem de erro na altura: 4 - 2 = 2px (mínimo) e 4 + 2 = 6px (máximo)
    altura_min = 2
    altura_max = 6

    def pixel_corresponde(px):
        r, g, b = px[:3]
        return (abs(r - cor_alvo[0]) <= tolerancia and 
                abs(g - cor_alvo[1]) <= tolerancia and 
                abs(b - cor_alvo[2]) <= tolerancia)

    def linha_valida(y_pos):
        if y_pos < 0 or y_pos >= altura:
            return False
        for x in range(x_inicio, x_fim + 1):
            if not pixel_corresponde(pixels[x, y_pos]):
                return False
        return True

    # Percorre do fundo até o meio da imagem (altura // 2)
    y = altura - 1
    limite_superior = altura // 2

    while y >= limite_superior:
        if linha_valida(y):
            # Conta a altura de linhas consecutivas que contêm o padrão de 25px
            altura_bloco = 0
            y_atual = y
            while y_atual >= limite_superior and linha_valida(y_atual):
                altura_bloco += 1
                y_atual -= 1

            # Confere se a altura encontrada atende à margem estipulada (2 a 6 pixels)
            if altura_min <= altura_bloco <= altura_max:
                posicao_corte = y_atual  # Posição imediatamente acima da faixa
                print(f"Faixa encontrada entre y={y_atual + 1} e y={y} (altura: {altura_bloco}px). Cortando em y={posicao_corte}")
                return max(0, posicao_corte)
            
            y = y_atual
        else:
            y -= 1

    return None

def processar_imagens(pasta_origem, pasta_destino, cor_alvo):
    """
    Processa todas as imagens da pasta origem, recortando as que têm o padrão visual inferior
    e copiando todas para a pasta destino.
    """
    os.makedirs(pasta_destino, exist_ok=True)
    
    arquivos = [f for f in os.listdir(pasta_origem) 
                if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff'))]
    
    print(f"Encontrados {len(arquivos)} arquivos para processar")
    
    for arquivo in arquivos:
        caminho_origem = os.path.join(pasta_origem, arquivo)
        caminho_destino = os.path.join(pasta_destino, arquivo)
        
        try:
            with Image.open(caminho_origem) as imagem:
                print(f"\nProcessando: {arquivo} ({imagem.width}x{imagem.height})")
                
                # Procura pela faixa usando a função corrigida
                posicao_corte = encontrar_faixa_inferior(imagem, cor_alvo)
                
                if posicao_corte is not None and posicao_corte > 0:
                    area_corte = (0, 0, imagem.width, posicao_corte)
                    imagem_recortada = imagem.crop(area_corte)
                    imagem_recortada.save(caminho_destino)
                    print(f"✓ Imagem recortada: {imagem_recortada.width}x{imagem_recortada.height}")
                else:
                    shutil.copy2(caminho_origem, caminho_destino)
                    print(f"✓ Imagem mantida original (sem faixa detectada)")
                    
        except Exception as e:
            print(f"✗ Erro ao processar {arquivo}: {e}")
            try:
                shutil.copy2(caminho_origem, caminho_destino)
                print(f"✓ Arquivo copiado mesmo com erro")
            except:
                print(f"✗ Não foi possível copiar o arquivo")

if __name__ == "__main__":
    pasta_origem = "./questoẽs"
    pasta_destino = "finalizadas"
    cor_alvo = (35, 31, 32)  # Cor informada RGB(35, 31, 32)
    
    print("Iniciando processamento de imagens...")
    print(f"Pasta origem: {pasta_origem}")
    print(f"Pasta destino: {pasta_destino}")
    print(f"Cor alvo: RGB{cor_alvo}")
    
    if not os.path.exists(pasta_origem):
        print(f"Erro: A pasta '{pasta_origem}' não existe!")
        exit(1)
    
    processar_imagens(pasta_origem, pasta_destino, cor_alvo)
    
    print("\n" + "="*50)
    print("Processamento concluído!")
    print(f"Todas as imagens foram salvas em: {pasta_destino}")