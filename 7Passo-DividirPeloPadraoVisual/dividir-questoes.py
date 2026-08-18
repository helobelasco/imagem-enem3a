from PIL import Image
import os

def converter_cor_gimp_para_rgb(gimp_r, gimp_g, gimp_b):
    """
    Converte valores do GIMP (0-100) para RGB (0-255)
    """
    r = int((gimp_r / 100) * 255)
    g = int((gimp_g / 100) * 255)
    b = int((gimp_b / 100) * 255)
    return (r, g, b)

def verificar_faixa_cor(pixels, x, y_inicio, altura, cor_alvo, tolerancia=15):
    """
    Verifica se uma sequência vertical de pixels possui a cor alvo
    """
    for dy in range(altura):
        pixel = pixels[x, y_inicio + dy]
        r, g, b = pixel[:3]
        if (abs(r - cor_alvo[0]) > tolerancia or 
            abs(g - cor_alvo[1]) > tolerancia or 
            abs(b - cor_alvo[2]) > tolerancia):
            return False
    return True

def encontrar_padrao_vertical(imagem, tolerancia=15):
    """
    Encontra o padrão vertical: 15px (35,31,32) + 9px (255,255,255) + 5px (35,31,32)
    Com margem de erro de ±3px em cada faixa.
    """
    largura, altura = imagem.size
    pixels = imagem.load()
    
    cor_1 = (35, 31, 32)
    cor_2 = (255, 255, 255)
    cor_3 = (35, 31, 32)
    
    posicoes_corte = []
    coluna_x = largura - 1  # Último pixel da direita
    
    y = 0
    # Limite considerando tamanhos mínimos do padrão
    while y < altura - (12 + 6 + 2):
        padrao_encontrado = False
        
        # Testa margens de erro (±3px) para a 1ª faixa (15px -> 12 a 18px)
        for h1 in range(12, 19):
            if not verificar_faixa_cor(pixels, coluna_x, y, h1, cor_1, tolerancia):
                continue
                
            # Testa margens de erro (±3px) para a 2ª faixa (9px -> 6 a 12px)
            for h2 in range(6, 13):
                if not verificar_faixa_cor(pixels, coluna_x, y + h1, h2, cor_2, tolerancia):
                    continue
                    
                # Testa margens de erro (±3px) para a 3ª faixa (5px -> 2 a 8px)
                for h3 in range(2, 9):
                    if (y + h1 + h2 + h3) <= altura and verificar_faixa_cor(pixels, coluna_x, y + h1 + h2, h3, cor_3, tolerancia):
                        
                        # Corte 10 pixels antes do padrão para mantê-los no início do corte
                        posicao_corte = y - 10
                        if posicao_corte < 0:
                            posicao_corte = 0
                            
                        posicoes_corte.append(posicao_corte)
                        tamanho_total_padrao = h1 + h2 + h3
                        print(f"Padrão encontrado em y={y} (faixas: {h1}px, {h2}px, {h3}px), cortando em y={posicao_corte}")
                        
                        y += tamanho_total_padrao
                        padrao_encontrado = True
                        break
                if padrao_encontrado:
                    break
            if padrao_encontrado:
                break
                
        if not padrao_encontrado:
            y += 1
            
    return posicoes_corte

def dividir_imagem_por_faixas(caminho_imagem, pasta_saida):
    """
    Divide a imagem verticalmente com base no padrão visual encontrado
    """
    imagem = Image.open(caminho_imagem)
    largura, altura = imagem.size
    
    print(f"Imagem carregada: {largura}x{altura} pixels")
    
    posicoes_corte = encontrar_padrao_vertical(imagem)
    
    if not posicoes_corte:
        print("Nenhum padrão visual encontrado na imagem!")
        return
        
    print(f"Encontradas {len(posicoes_corte)} ocorrências do padrão para corte")
    
    os.makedirs(pasta_saida, exist_ok=True)
    
    posicao_anterior = 0
    
    for i, posicao_corte in enumerate(posicoes_corte):
        if posicao_corte <= posicao_anterior:
            continue
            
        area_corte = (0, posicao_anterior, largura, posicao_corte)
        secao = imagem.crop(area_corte)
        
        nome_arquivo = f"parte_{i+1:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo: {caminho_completo} ({secao.width}x{secao.height}px)")
        
        posicao_anterior = posicao_corte
        
    if posicao_anterior < altura:
        area_corte = (0, posicao_anterior, largura, altura)
        secao = imagem.crop(area_corte)
        
        nome_arquivo = f"parte_{len(posicoes_corte)+1:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo: {caminho_completo} ({secao.width}x{secao.height}px)")

if __name__ == "__main__":
    caminho_imagem = "pagina_enem_9.png"  # Substitua pelo caminho da sua imagem
    pasta_saida = "pg9"  # Substitua pelo nome da pasta de saída desejada
    
    dividir_imagem_por_faixas(caminho_imagem, pasta_saida)
    
    print("Divisão concluída!")