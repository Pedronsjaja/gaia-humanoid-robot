# Como se orientar no GitHub do Gaia

[Voltar ao início](../README.md)

Você não precisa saber programar para ler guias, baixar CADs ou contribuir com uma medição.

## Encontrar os arquivos

O **README** é a página inicial do projeto, mostrada abaixo da lista de arquivos. Clique nos links azuis e escolha sua frente: programação, estrutura ou eletrônica. Pastas agrupam assuntos; clicar no nome de uma pasta abre seu conteúdo. Use os nomes no topo para voltar ou o link **Início** dos guias.

| Nome no GitHub | Significado |
| --- | --- |
| Repository/repositório | Pasta do projeto com histórico |
| README.md | Página explicativa; .md é texto formatado |
| Code | Arquivos e opções de download/clone |
| Issues | Registro de problemas, dúvidas e tarefas |
| Pull Requests | Propostas de alteração para revisão |
| Actions | Execuções automáticas de verificações |
| Commit | Registro de uma mudança |
| Branch | Linha de trabalho sem editar diretamente a principal |
| main | Versão principal publicada |

## Baixar

**Projeto inteiro:** clique em **Code → Download ZIP**. Extraia o ZIP antes de abrir scripts ou montagens CAD. Ele é uma cópia do momento; mudanças posteriores no site não atualizam a pasta baixada.

**Arquivo individual:** abra o arquivo e procure **Download raw file**/ícone de download. Se o GitHub disser que não mostra o formato, baixe e abra no programa apropriado. Arquivos SolidWorks de montagem precisam também das peças referenciadas; nesse caso, baixe a pasta completa pelo ZIP.

**Clone:** quem vai trabalhar com Git pode usar:

```bash
git clone https://github.com/Pedronsjaja/gaia-lx225-buslinker.git
```

O clone inclui histórico e permite atualizar/enviar alterações; o ZIP não. Para atualizar um clone sem mudanças locais pendentes, use `git pull --ff-only`. Se houver erro, consulte o responsável; não apague sua pasta ou force a atualização.

## Executar comandos dos guias

Um bloco marcado **bash** é para o Terminal Linux; **powershell** é para Windows. Não cole no campo de pesquisa do GitHub. Leia o pré-requisito e substitua exemplos como `COM7` pelo valor do seu computador. Comando de movimento pode atuar no robô quando o guia for de bancada real; o laboratório Gazebo usa apenas o robô virtual.

## Relatar problema ou sugerir melhoria

Em **Issues → New issue**, escreva um título específico: “V3 aparece na COM7, mas ID 1 não responde”. Inclua:

- Guia/etapa e comando executado.
- Comportamento esperado e observado.
- Sistema, revisão do equipamento/modelo e mensagem completa.
- Foto ou captura quando ajudar.

Não publique senhas, chaves privadas, tokens ou dados pessoais nos logs. Ler e baixar repositório público não exige conta; abrir Issue e propor mudanças exige login.

## Propor uma alteração

Para uma correção curta, use o lápis de edição quando disponível e escolha criar uma branch/proposta. Se não tiver acesso de escrita, o GitHub pode oferecer um **fork**, sua cópia para propor mudanças ao projeto original.

Quem usa Git localmente deve criar uma branch, editar, conferir o diff, testar e abrir um Pull Request. Descreva o motivo, os arquivos alterados e como verificou. Peças CAD também precisam explicar revisão e compatibilidade da montagem.

O indicador verde em Actions significa que aqueles testes passaram; não certifica eletrônica, resistência mecânica ou elegibilidade na CBR.

## Por onde começar na equipe

| Perfil | Primeiro caminho |
| --- | --- |
| Nunca usei Linux/ROS | [Ambiente Ubuntu/ROS 2](https://github.com/Pedronsjaja/gaia-ros2-ubuntu24) |
| Vou programar o robô | [Programação](https://github.com/Pedronsjaja/gaia-humanoid-simulation/blob/main/docs/programacao/README.md) |
| Vou desenhar/imprimir peças | [Estrutura](https://github.com/Pedronsjaja/gaia-humanoid-structure/blob/main/docs/estrutura/README.md) |
| Vou ligar placas e servos | [Eletrônica](eletronica/README.md) |
| Vou organizar a participação na CBR | [Competição](https://github.com/Pedronsjaja/gaia-humanoid-structure/blob/main/docs/competicao/README.md) |
