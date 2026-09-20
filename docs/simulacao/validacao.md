# Registro de validação do laboratório

[Índice](README.md) · [Versões e fontes](referencias.md)

## Verificado em 20/09/2026

No Windows do mantenedor, sem ROS/Gazebo instalado:

- Expansão do Xacro da revisão ROBOTIS fixada no manifesto.
- Cinco testes do adaptador: preservação das juntas/geometria/inércias; base presa/livre; correspondência das 20 juntas e controladores; rejeição de modelo alterado/duplicado; sensores e tópicos da ponte.
- Análise de sintaxe Python e leitura de configurações XML/YAML.
- 47 testes da bancada Python com serial simulada.
- Verificação dos destinos dos links relativos Markdown.

A [ação de compilação Linux](https://github.com/Pedronsjaja/gaia-humanoid-robot/actions/workflows/simulation.yml) instala dependências Jazzy, compila os pacotes e executa os testes do modelo. **Ela não executa a física nem valida a renderização dos sensores.** Veja o resultado de cada execução; a existência do arquivo de workflow não significa aprovação.

## Ensaio pendente no computador da equipe

Execute o [tutorial](instalacao-e-laboratorio.md) e anexe à Issue uma ficha:

| Campo | Preencher após o ensaio |
| --- | --- |
| Pessoa/data | — |
| CPU, RAM, GPU/driver | — |
| Ubuntu e ROS | — |
| Dual boot ou VM/versão | — |
| Commit Gaia e revisão OP3 | — |
| Compilação e logs | — |
| Modelo visível e base presa | — |
| Controladores ativos e 20 juntas | — |
| head_pan atinge 0,15 rad e retorna | — |
| Imagem, CameraInfo e frames coerentes | — |
| IMU em repouso e durante movimento | — |
| Taxas e fator de tempo real observados | — |
| Encerramento sem processos residuais | — |

Não registre “aprovado” apenas porque a janela abriu. Compare alvos e leituras; confira a direção da câmera e as malhas. Marcha, equilíbrio, modelo físico LX-225 e futebol autônomo exigem ensaios adicionais.
