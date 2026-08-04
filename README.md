# BrAIn 🧠
**### Assistente Inteligente para Organização e Busca de Documentos utilizando IA Local**

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
- ✅ Modelagem orientada a objetos utilizando a entidade `Document`.
- ✅ Testes automatizados para scanner, indexador e persistência.
- ✅ Arquitetura modular preparada para expansão.

---

## Arquitetura do Sistema

O fluxo implementado atualmente é:

```text
Configuração → Indexer → Scanner → DocumentRepository → SQLite
```

A imagem abaixo representa a arquitetura-alvo do projeto, incluindo os módulos de IA e interface ainda planejados.

![Visão Geral da Arquitetura do BrAIn](assets/image.png)

---

## Stack Tecnológico

**Backend & Estrutura**
* **Linguagem:** Python
* **Paradigma:** Programação Orientada a Objetos (POO) e Clean Code
* **Ambiente & Gestão:** uv, Git, GitHub

**Inteligência Artificial**
* **Modelo planejado:** Gemma (Google)
* **Engine planejada:** Ollama (processamento 100% local)

**Banco de Dados & Interface**
* **Memória Central:** SQLite
* **Frontend planejado:** Python Desktop GUI

---

## Executando o projeto

Na raiz do projeto, execute:

```powershell
python -m app.main
```

As pastas monitoradas são definidas em `config/settings.json`. O BrAIn apenas lê os arquivos encontrados e persiste seus metadados em `data/brain.db`; ele não move, renomeia ou modifica os documentos.

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
- [ ] Detecção de arquivos removidos

### Fase 3 - Inteligência Artificial
- [ ] Integração com Ollama
- [ ] Integração com Gemma
- [ ] Classificação automática
- [ ] Resumos automáticos
- [ ] Busca semântica

### Fase 4 - Interface Desktop
- [ ] Dashboard
- [ ] Pesquisa
- [ ] Histórico
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
- Testes automatizados

### Em desenvolvimento

- Busca
- Extração de conteúdo
- IA Local
---

** Autor**

**Sandro Monteiro**
*Desenvolvedor RPA*
