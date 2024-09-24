# Dashboard Python Users

Este projeto implementa um **Dashboard** para análise de dados de usuários, utilizando as bibliotecas do Python para processamento de dados e visualização. O objetivo do projeto é coletar, processar e visualizar informações dos usuários de forma intuitiva e acessível.

## Funcionalidades

- Visualização de gráficos de usuários por meio de dashboards interativos.
- Processamento de dados de usuários utilizando `pandas` e `numpy`.
- Geração de gráficos com a biblioteca `matplotlib`.
- Interface gráfica amigável com `Tkinter` para navegação no dashboard.

## Tecnologias Utilizadas

O projeto foi desenvolvido utilizando as seguintes tecnologias:

- **Python**: Linguagem de programação principal utilizada no projeto.
- **Tkinter**: Biblioteca usada para criar a interface gráfica do usuário.
- **Matplotlib**: Biblioteca utilizada para gerar gráficos e visualizações de dados.
- **Pandas**: Para manipulação e análise de dados tabulares.
- **Numpy**: Para suporte ao cálculo numérico.
  
## Estrutura do Projeto

    dashboard-python-users/
    │
    ├── main.py               # Arquivo principal que executa o dashboard
    ├── data/                 # Diretório contendo os arquivos de dados
    │   └── users_data.csv     # Exemplo de arquivo CSV com dados de usuários
    ├── modules/              # Módulos auxiliares para processamento e visualização
    │   ├── data_processing.py # Módulo para carregar e processar dados
    │   └── plot_utils.py      # Módulo com funções para criação de gráficos
    ├── assets/               # Arquivos estáticos como imagens e ícones
    │   └── logo.png           # Logo do dashboard
    └── README.md             # Este arquivo


## Instalação

Para executar este projeto localmente, siga as etapas abaixo:

1. **Clone o repositório**:
   ```bash
   git clone https://github.com/Arthurrfreire/dashboard-python-users.git

**Navegue até o diretório do projeto:**

    cd dashboard-python-users

**Crie um ambiente virtual (opcional, mas recomendado):**

    python -m venv venv
    source venv/bin/activate   # No Windows: venv\Scripts\activate

**Instale as dependências:**

    pip install -r requirements.txt

**Execute o projeto:**

    python main.py

## Como Usar
Após executar o projeto, o dashboard será exibido. Ele permite a visualização de gráficos e estatísticas sobre os usuários fornecidos no arquivo users_data.csv. Você pode carregar novos arquivos de dados, gerar gráficos interativos e visualizar diferentes métricas relacionadas aos usuários.

# Funcionalidades principais:

**Carregar dados:** Escolha um arquivo CSV para carregar dados de usuários.

![Tela de login](https://i.imgur.com/01BMqK3.png)

**Visualizar gráficos:** Geração automática de gráficos interativos com base nos dados carregados.

![Tela de login](https://i.imgur.com/vPgO1Z6.png)

**Análise de métricas:** Visualize métricas como distribuição de idade, gênero, localização, entre outros.

![Tela de login](https://i.imgur.com/XE0y9Y5.png)

## Contribuições

Contribuições são bem-vindas! Se você deseja melhorar este projeto, sinta-se à vontade para seguir os seguintes passos:

1. Fork o repositório.
2. Crie uma branch com sua feature (git checkout -b minha-feature).
3. Commit suas mudanças (git commit -m 'Adiciona nova feature').
4. Push a branch (git push origin minha-feature).
5. Abra um Pull Request.

## Licença

    Este projeto está licenciado sob a licença MIT. Consulte o arquivo LICENSE para obter mais informações.

