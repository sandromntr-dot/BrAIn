# BrAIn 🧠
### Assistente inteligente para organização e busca de documentos com IA local

O BrAIn é um assistente inteligente projetado para a organização, gerenciamento e localização de documentos utilizando Inteligência Artificial executada 100% localmente.

A proposta é oferecer uma solução definitiva para ajudar usuários e empresas a encontrarem documentos perdidos ou desorganizados em suas próprias máquinas, garantindo total privacidade, segurança e controle dos dados (alinhado às boas práticas de governança e LGPD).

---

## O Problema
Diariamente, milhares de arquivos são criados, baixados e compartilhados:

* 📄 PDFs e Documentos de texto
* 📊 Planilhas e Apresentações
* 📘 Manuais e Procedimentos operacionais
* 📑 Atas e Relatórios

Com a correria do dia a dia, a grande maioria acaba se perdendo num "buraco negro" chamado pasta Downloads ou em diretórios sem a devida organização. Muitas vezes, você lembra perfeitamente do contexto e do conteúdo do arquivo, mas o nome ou o local exato viram um mistério.

> *"Preciso encontrar aquele PDF com o procedimento de instalação que baixei há alguns meses... Cadê?"*

O BrAIn resolve esse problema combinando indexação inteligente de metadados e o poder da IA local.

---

## Objetivo do MVP
Criar um assistente local leve e eficiente, capaz de:

* 🔍 Monitorar e identificar novos arquivos no computador.
* 🗂️ Organizar informações estruturadas e extrair contexto.
* 💾 Armazenar metadados de forma segura e local.
* 🧠 Permitir buscas inteligentes baseadas em linguagem natural.
* 🖥️ Auxiliar o usuário através de uma interface intuitiva.

---

## Funcionalidades implementadas

Atualmente o BrAIn já é capaz de:

- ✅ Detectar automaticamente pastas padrão do Windows (Downloads, Documents e Desktop).
- ✅ Permitir configuração das pastas monitoradas através de arquivo JSON.
- ✅ Escanear pastas e subpastas recursivamente.
- ✅ Continuar a indexação quando um arquivo ou diretório não puder ser lido.
- ✅ Coletar metadados dos documentos:
  - Nome
  - Caminho
  - Extensão
  - Tamanho em bytes
  - Data de criação
- ✅ Persistir os metadados localmente em SQLite.
- ✅ Impedir duplicações utilizando o caminho do arquivo como identificador único.
- ✅ Atualizar documentos incrementalmente quando seus metadados mudarem.
- ✅ Marcar documentos removidos como indisponíveis sem apagar seu histórico.
- ✅ Pesquisar por nome, caminho, extensão, resumo e categoria.
- ✅ Combinar busca textual e semântica com embeddings locais persistidos.
- ✅ Extrair conteúdo de arquivos TXT, DOCX, PDFs textuais, CSV, BPMN e PPTX.
- ✅ Analisar imagens, PDFs digitalizados e PPTX baseados em imagens com Gemma
  Vision através do Ollama local.
- ✅ Processar documentos visuais página a página, com checkpoints SQLite e
  retomada sem repetir páginas concluídas.
- ✅ Gerar resumos e categorias com Gemma 4 através do Ollama local.
- ✅ Processar automaticamente os documentos pendentes, com pausa, retomada e
  tolerância a falhas, ou analisar um documento selecionado.
- ✅ Pesquisar e visualizar resultados em uma interface Tkinter.
- ✅ Exibir dashboard compacto com indicadores de disponibilidade e análise.
- ✅ Consultar o histórico local de análises concluídas e falhas.
- ✅ Modelagem orientada a objetos utilizando a entidade `Document`.
- ✅ Testes automatizados para scanner, indexador, persistência, extração e IA.
- ✅ Arquitetura modular preparada para expansão.

---

## Arquitetura do Sistema

O fluxo implementado atualmente é:

```text
Configuração → Scanner → Indexer → DocumentRepository → SQLite
                                           ↑              ↓
Tkinter → SearchService / AnalysisService → Gemma 4 ← Ollama
```

A imagem abaixo representa a visão geral que orientou a arquitetura do projeto.

![Visão Geral da Arquitetura do BrAIn](assets/image.png)

---

## Stack Tecnológico

**Backend & Estrutura**
* **Linguagem:** Python
* **Paradigma:** Programação Orientada a Objetos (POO) e Clean Code
* **Ambiente & Gestão:** uv, Git, GitHub

**Inteligência Artificial**
* **Modelos:** Gemma 4 8B para texto e Gemma 3 4B para visão, executados localmente
* **Embeddings:** EmbeddingGemma via Ollama para busca semântica local
* **Engine:** Ollama
* **Saída estruturada:** resumo e categoria em JSON
* **Visão:** leitura e interpretação local de imagens e documentos digitalizados

**Banco de Dados & Interface**
* **Memória Central:** SQLite
* **Frontend:** Tkinter/ttk
* **Extração de PDF:** pypdf
* **Renderização de PDF para visão:** PyMuPDF

---

## Executando o projeto

Na raiz do projeto, execute:

```powershell
python -m app.main
```

As pastas monitoradas são definidas em `config/settings.json`. O BrAIn apenas lê os arquivos encontrados e persiste seus metadados em `data/brain.db`; ele não move, renomeia ou modifica os documentos.

Para utilizar a análise local, mantenha o Ollama em execução e instale o modelo configurado:

```powershell
ollama list
ollama run gemma4:latest
ollama pull gemma3:4b
ollama pull embeddinggemma
```

Na interface, utilize **Analisar documentos pendentes** para executar a primeira
carga ou retomar a fila. O painel de atividade mostra o arquivo atual, o tempo
decorrido e os contadores de sucessos, falhas e itens pendentes. Utilize **Pausar
após o atual** para interromper com segurança depois que o documento em andamento
terminar. Também é possível selecionar uma linha compatível e utilizar **Analisar
selecionado**.

Os formatos analisáveis atualmente são `.txt`, `.docx`, `.pdf`, `.csv`, `.bpmn`,
`.pptx`, `.jpg`, `.jpeg`, `.png` e `.webp`. Quando um PDF ou PPTX não contém
texto extraível, o BrAIn envia suas páginas ou imagens ao Gemma Vision através do
Ollama. Cada resultado é persistido imediatamente; arquivos com erro são
registrados e ignorados pela execução automática seguinte.

Documentos visuais são processados uma página ou slide por vez. O resumo parcial
de cada página é salvo no SQLite e reutilizado em uma nova tentativa caso a
aplicação seja encerrada antes da consolidação final.

A pesquisa combina correspondências textuais com similaridade semântica nos
documentos já analisados. Os embeddings são criados localmente na primeira busca
e armazenados no SQLite para reutilização. Se o Ollama ou o modelo
`embeddinggemma` não estiver disponível, a pesquisa continua automaticamente no
modo textual.

Para executar os testes automatizados:

```powershell
python -m unittest discover -s tests -v
```

---

## Princípios de Engenharia de Software
O desenvolvimento deste projeto é guiado pelas melhores práticas de engenharia:

* **Código Limpo (Clean Code):** Nomes de variáveis descritivos e funções objetivas.
* **Arquitetura Modular:** Separação clara de responsabilidades.
* **Baixo Acoplamento:** Módulos independentes e facilmente testáveis.
* **Privacidade by Design:** Nenhum dado sensível sai da máquina do usuário.

---

## Roadmap

### Fase 1 - Fundação e Estrutura
- [x] Configuração inicial do projeto
- [x] Ambiente Python com uv
- [x] Estrutura modular
- [x] Organização por camadas

### Fase 2 - Núcleo do Sistema (Core)
- [x] Entidade Document
- [x] Scanner de arquivos
- [x] Scanner recursivo com tolerância a falhas de leitura
- [x] Configuração dinâmica das pastas monitoradas
- [x] Indexação inicial de metadados
- [x] Persistência em SQLite
- [x] Atualização incremental da base
- [x] Prevenção de registros duplicados por caminho
- [x] Testes automatizados do núcleo implementado
- [x] Detecção reversível de arquivos removidos

### Fase 3 - Inteligência Artificial
- [x] Integração com Ollama
- [x] Integração com Gemma 4
- [x] Classificação assistida
- [x] Resumos assistidos
- [x] Extração de TXT, DOCX, PDF textual, CSV, BPMN e PPTX
- [x] Análise visual de imagens, PDFs digitalizados e PPTX baseados em imagens
- [x] Reconhecimento visual de PDFs digitalizados com Gemma Vision
- [x] Processamento em lote com progresso, pausa e controle de falhas
- [x] Checkpoints e retomada da análise visual por página/slide
- [x] Busca semântica

### Fase 4 - Interface Desktop
- [x] Interface inicial em Tkinter
- [x] Pesquisa por metadados
- [x] Exibição de resumo e categoria
- [x] Análise do documento selecionado
- [x] Monitor de atividade da análise em lote
- [x] Dashboard de documentos e análises
- [x] Histórico
- [ ] Estatísticas

### Fase 5 - RAG
- [ ] Embeddings
- [ ] Base Vetorial
- [ ] Chat com documentos
---

## Segurança e Privacidade
O BrAIn nasceu com o princípio fundamental do processamento estritamente local.
Isso significa que seus manuais, contratos, planilhas e relatórios permanecem 100% no seu ambiente. A aplicação evita o envio de qualquer informação sensível para APIs externas ou serviços em nuvem, garantindo governança total dos seus dados.

---

## 🚧 Status do Projeto

Versão atual: **MVP em desenvolvimento ativo**

### Implementado

- Estrutura do projeto
- Arquitetura modular
- Scanner de arquivos
- Configuração dinâmica das pastas monitoradas
- Coleta de metadados
- Persistência local em SQLite
- Atualização incremental e prevenção de duplicações
- Scanner recursivo com relatório de falhas
- Detecção reversível de documentos removidos
- Busca local por metadados
- Interface desktop em Tkinter
- Integração local com Ollama e Gemma 4
- Extração e análise de TXT, DOCX, PDFs textuais, CSV, BPMN e PPTX
- Resumos e categorias persistidos no SQLite
- Primeira carga automática com progresso, pausa, retomada e tolerância a falhas
- Testes automatizados

### Em desenvolvimento

- Aprimoramento da pausa durante documentos visuais extensos
- Aprimoramento da busca semântica e RAG

### Limitações atuais

- A análise visual de documentos extensos pode levar bastante tempo em CPU.
- O formato binário antigo `.ppt` exige conversão prévia para `.pptx` ou `.pdf`.
- A análise com Gemma pode levar alguns minutos quando executada somente em CPU.
- O conteúdo enviado ao modelo é limitado a 6.000 caracteres por documento.
---

** Autor**

**Sandro Monteiro**
*Desenvolvedor RPA*
