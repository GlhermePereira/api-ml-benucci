
## **1. Objetivo**

Implementar um serviço de recomendações que retorne produtos similares ao produto consultado, garantindo desempenho, escalabilidade e isolamento por categoria.

---

## **2. Funcionalidades Principais**

### **2.1. API de Recomendação**

- Endpoint: `GET /recommendations`
    
- Parâmetros obrigatórios:
    
    - `product_id`
        
    - `category_id`
        
- Parâmetros opcionais:
    
    - subcategoria, tags, faixa de preço, marca, limite de resultados.
        
- Retorno:
    
    - Lista ordenada de produtos similares (default: top 10).
        

---

## **3. Lógica de Recomendação**

### **3.1. Validação**

- Verificar se `product_id` existe.
    
- Verificar se `category_id` corresponde ao produto.
    
- Validar filtros opcionais.
    
- Respostas esperadas:
    
    - 400 para parâmetros inválidos.
        
    - 404 para produto ou categoria inexistente.
        

### **3.2. Seleção de Produtos**

- Consultar banco de dados por produtos da mesma categoria.
    
- Excluir `product_id`.
    
- Aplicar filtros adicionais, quando informados.
    

### **3.3. Embeddings**

- Modelo de embeddings carregado no startup.
    
- Estratégia híbrida:
    
    - **Cache em memória** (rápido).
        
    - **Persistência** (MongoDB / arquivo NPZ).
        
- Fluxo:
    
    1. Tentar carregar embedding do cache.
        
    2. Se não existir, carregar persistido.
        
    3. Se não existir, gerar embedding e persistir.
        
- Atualização incremental:
    
    - Gerar embeddings apenas para produtos novos ou modificados.
        

### **3.4. Cálculo de Similaridade**

- Montar vetor do produto base + candidatos.
    
- Calcular similaridade (distância do cosseno).
    
- Ordenar pelo maior grau de similaridade.
    
- Selecionar top N (default: 10).
    

---

## **4. Arquitetura e Performance**

### **4.1. Cache**

- Estrutura: `{category_id: {product_id: embedding}}`
    
- Estratégias recomendadas:
    
    - Expiração por tempo.
        
    - LRU (Least Recently Used) para categorias pouco usadas.
        

### **4.2. Persistência**

- Armazenar embeddings pré-calculados em banco ou arquivos.
    
- Pré-carregar apenas categorias mais acessadas durante o startup.
    

### **4.3. Escalabilidade**

- Suporte a milhares de produtos por categoria.
    
- Cálculos vetorizados (NumPy/Torch).
    
- Possibilidade futura de FAISS/Annoy/HNSWlib para reduzir latência.
    

---

## **5. Entregáveis**

### **MVP (Versão Inicial)**

1. Endpoint `/recommendations` funcional.
    
2. Filtros básicos: categoria, preço, tags.
    
3. Embeddings gerados sob demanda.
    
4. Cache em memória.
    
5. Similaridade via NumPy.
    
6. Retorno do top 10.
    

### **Versão 1.1 (Otimização)**

1. Persistência de embeddings (Mongo/NPZ).
    
2. Pré-carregamento de modelo no startup.
    
3. Atualização incremental automática.
    

### **Versão 1.2 (Escala)**

1. Indexação vetorial com FAISS/Annoy para categorias grandes.
    
2. Logs e métricas de performance.
    
3. Painel básico de monitoramento.
    

### **Versão 2.0 (Expansão)**

1. Recomendação cross-category opcional.
    
2. Combinação de embeddings (texto + atributos).
    
3. Recomendação híbrida (regras + ML).