Comando base que roda o simulador

    ros2 launch sprint_sbr master.launch.py



Argumentos disponíveis:

    num_boats: Quantidade de barcos que você quer spawnar (o padrão é 1). O código já nomeia eles em ordem (alfa, bravo, charlie...) e enfileira todo mundo certinho para não nascer um em cima do outro.

    world_name: O nome do mundo que vai carregar no Gazebo (o padrão é ocean). Se for usar o de competição, é só passar "sydney_regatta" aqui.

    positions: Se quiser que os barcos nasçam em lugares específicos em vez da fila automática, você passa as coordenadas aqui usando o formato "x,y; x,y". O script já calcula o offset do mapa automaticamente.

Exemplos práticos

Rodar no mapa de Sydney com 3 barcos (eles vão nascer alinhados perto das tendas):

    ros2 launch sprint_sbr master.launch.py world_name:=sydney_regatta num_boats:=3

Rodar com 2 barcos escolhendo as posições na mão:   

    ros2 launch sprint_sbr master.launch.py num_boats:=2 positions:="5.0, 0.0; -5.0, 10.0"