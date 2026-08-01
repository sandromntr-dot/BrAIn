# BrAIn

## Local AI Document Assistant

O BrAIn é um assistente inteligente para organização, gerenciamento e localização de documentos utilizando Inteligência Artificial local.

A proposta é criar uma solução que ajude usuários e empresas a encontrarem documentos perdidos ou desorganizados dentro de seus próprios computadores, mantendo privacidade, segurança e controle dos dados.

---

# O problema

Diariamente milhares de documentos são criados, baixados e compartilhados:

- PDFs;
- planilhas;
- apresentações;
- documentos de texto;
- manuais;
- procedimentos operacionais;
- atas;
- relatórios.

Com o tempo, arquivos importantes acabam perdidos em pastas, downloads e diretórios sem uma organização adequada.

Muitas vezes o usuário lembra do conteúdo do documento, mas não lembra o nome do arquivo.

Exemplo:

> "Preciso encontrar aquele PDF com o procedimento de instalação que baixei há alguns meses."

O BrAIn busca resolver esse problema utilizando indexação inteligente e IA local.

---

# Objetivo do MVP

Criar um assistente local capaz de:

- monitorar documentos no computador;
- identificar novos arquivos;
- organizar informações dos documentos;
- armazenar metadados localmente;
- permitir busca inteligente;
- auxiliar o usuário através de uma interface simples.

---

# Arquitetura

```text
BrAIn

├── Interface
│   └── Aplicação desktop
│
├── Core
│   ├── Scanner de arquivos
│   ├── Processamento
│   └── Organização
│
├── IA Local
│   └── Gemma via Ollama
│
├── Banco de Dados
│   └── SQLite
│
└── Dados
    └── Documentos e metadados locais

**# Tecnologias**
Backend
Python
Programação Orientada a Objetos
Clean Code
SQLite
Inteligência Artificial
Gemma
Ollama
Processamento local de dados
Interface
Python Desktop GUI
Gerenciamento
Git
GitHub
uv
Princípios do projeto

O desenvolvimento seguirá:

Código limpo;
Separação de responsabilidades;
Arquitetura modular;
Baixo acoplamento;
Programação Orientada a Objetos;
Privacidade dos dados.
Roadmap
Fase 1 - Estrutura inicial

[x] Configuração do projeto
[x] Ambiente Python com uv
[x] Estrutura de diretórios

Fase 2 - Núcleo do sistema

[ ] Criar entidade Document
[ ] Scanner de arquivos
[ ] Persistência SQLite
[ ] Cadastro de metadados

Fase 3 - Inteligência Artificial

[ ] Integração com Gemma
[ ] Classificação automática
[ ] Resumo de documentos
[ ] Busca inteligente

Fase 4 - Interface

[ ] Dashboard desktop
[ ] Lista de documentos
[ ] Pesquisa
[ ] Chat assistente

Segurança e privacidade

O BrAIn possui como princípio o processamento local.

Os documentos permanecem no ambiente do usuário, evitando o envio de informações sensíveis para serviços externos.

Status

🚧 Projeto em desenvolvimento

MVP sendo construído com foco em aprendizado, arquitetura de software e aplicação prática de Inteligência Artificial local.

Autor

Sandro Monteiro

Desenvolvedor RPA | Automação | IA