# Simulação do humanoide Gaia — referência ROBOTIS OP3

[Início do Gaia](../../README.md) · [Instalar Ubuntu e ROS 2](https://github.com/Pedronsjaja/gaia-ros2-ubuntu24)

A equipe usará o **ROBOTIS OP3 como referência de estudo** para organização mecânica, representação das juntas e software de humanoides. O primeiro laboratório usa o modelo OP3 oficial. O modelo definitivo do Gaia ainda precisa incorporar suas medidas, massas, sensores e servos LX-225.

## O que cada programa faz?

| Camada | Função |
| --- | --- |
| Ubuntu 24.04 | Sistema que executa ferramentas e drivers |
| ROS 2 Jazzy | Comunicação e organização dos programas robóticos |
| Gazebo Harmonic | Física, cenário e sensores virtuais |
| URDF/Xacro | Descrição de corpos, juntas, geometria e inércia |
| ros2_control | Interface entre controladores e juntas |
| RViz | Visualiza dados ROS; não calcula física |

A combinação Jazzy/Harmonic segue a [documentação Gazebo](https://gazebosim.org/docs/harmonic/ros_installation/). O manual OP3 possui abas **2025 ~** e **~ 2023**: a primeira apresenta ROS 2; a segunda contém comandos ROS 1 como `roslaunch` e `catkin`. Siga a versão ROS 2. [Manual de simulação OP3](https://emanual.robotis.com/docs/en/platform/op3/simulation/#simulation).

## Sequência para a equipe

| Etapa | Guia | Entrega |
| --- | --- | --- |
| 0 | [Ambiente Linux/ROS 2](https://github.com/Pedronsjaja/gaia-ros2-ubuntu24) | Talker/listener funcionando |
| 1 | [Instalar e executar o laboratório](instalacao-e-laboratorio.md) | OP3 no Gazebo, juntas, câmera e IMU |
| 2 | [Do CAD ao modelo Gaia](modelo-gaia.md) | Uma junta Gaia descrita e testada |
| 3 | [ROS 2 e autonomia](autonomia.md) | Plano de trabalho com critérios de avanço |
| Consulta | [Bibliotecas, revisões e limitações](referencias.md) | Saber o que reutilizar e o que adaptar |

## O que está entregue agora

O pacote [gaia_op3_sim](../../ros2/gaia_op3_sim/) adiciona um laboratório próprio ao modelo `op3_description` oficial, baixado por [manifesto com revisão fixa](../../simulation/op3.repos). Ele inclui suporte virtual, controle de posição das juntas, câmera/IMU ideais e ponte ROS/Gazebo. O cenário tem chão e uma caixa vermelha para exercícios de visão.

O padrão é **tronco preso ao mundo, a 0,6 m**, para não depender de equilíbrio ao aprender ROS. Isso não demonstra que o robô fica em pé sozinho. A opção de base livre serve para estudos posteriores e pode resultar em queda.

O laboratório **não carrega op3_manager**, não usa a BusLinker e não abre portas seriais. Não execute simultaneamente controladores do robô real no domínio usado para os exercícios.

## Por que um laboratório Gaia além do lançador oficial?

Na revisão inspecionada de `ROBOTIS-OP3-Common/jazzy-devel`, o Xacro principal tem a inclusão de configuração de simulação comentada e não gera `ros2_control`. O lançador oficial de simulação solicita controladores, mas o modelo dessa revisão não contém a integração correspondente. O adaptador daqui completa essa configuração em memória e mantém os arquivos ROBOTIS intactos. [Evidências e revisões](referencias.md).

A configuração do laboratório é didática. Limites do modelo OP3 e atuação ideal por posição não representam fielmente os motores LX-225. Marcha, equilíbrio e autonomia não estão implementados neste pacote.
