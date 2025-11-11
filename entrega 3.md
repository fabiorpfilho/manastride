Transformado asset loader em estático
Removido instanciações dele para chamar apenas no momento necessário sem mante-lo

Removido instanciações do spell system no level e entity manager, agora é instanciado no player e mantido lá, quando outra classe necessita acessa-lo chama através do player

Camera agora também é singleton para garantir que sempre terá apenas uma instnacia dela

Analisado e começado uma tentativa de transformar o level em um singleton, transição de fases quebrada já que o antigo método era reconstruir a instancia do level