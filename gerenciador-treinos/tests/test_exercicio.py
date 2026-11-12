import pytest

from models.exercicio import (Exercicio, ExercicioCardio, ExercicioIsometrico,
                              ExercicioMusculacao)


def test_exercicio_e_abstrato():
    with pytest.raises(TypeError):
        Exercicio("Qualquer", "Peito")


def test_volume_musculacao():
    supino = ExercicioMusculacao("Supino reto", "Peito", 4, 10, 40)
    assert supino.calcular_volume() == 1600


def test_volume_cardio():
    esteira = ExercicioCardio("Esteira", 30, 5)
    assert esteira.calcular_volume() == 30


def test_volume_isometrico():
    prancha = ExercicioIsometrico("Prancha", "Abdômen", 3, 45)
    assert prancha.calcular_volume() == 135


def test_descricoes():
    assert ExercicioMusculacao("Supino", "Peito", 4, 10, 40).descricao() == \
        "Supino (Peito): 4x10 com 40 kg"
    assert ExercicioCardio("Esteira", 30, 5).descricao() == \
        "Esteira (Cardio): 30 min, 5 km"
    assert ExercicioCardio("Bike", 15).descricao() == "Bike (Cardio): 15 min"
    assert ExercicioIsometrico("Prancha", "Abdômen", 3, 45).descricao() == \
        "Prancha (Abdômen): 3x45 s"


def test_polimorfismo_volume():
    exercicios = [
        ExercicioMusculacao("Supino", "Peito", 4, 10, 40),
        ExercicioCardio("Esteira", 30),
        ExercicioIsometrico("Prancha", "Abdômen", 3, 45),
    ]
    # O mesmo método, chamado do mesmo jeito, dá um resultado diferente em cada tipo.
    assert [e.calcular_volume() for e in exercicios] == [1600, 30, 135]
    assert all(isinstance(e, Exercicio) for e in exercicios)


def test_aceita_numeros_em_texto():
    supino = ExercicioMusculacao("Supino", "Peito", "4", "10", "42,5")
    assert supino.carga_kg == 42.5


@pytest.mark.parametrize("series, repeticoes, carga", [
    (-1, 10, 40),   # séries negativas
    (0, 10, 40),    # zero séries
    (4, 2.5, 40),   # repetição quebrada
    (4, 10, -5),    # carga negativa
    (4, "dez", 40), # texto que não é número
])
def test_musculacao_valores_invalidos(series, repeticoes, carga):
    with pytest.raises(ValueError):
        ExercicioMusculacao("Supino", "Peito", series, repeticoes, carga)


def test_nome_vazio_invalido():
    with pytest.raises(ValueError):
        ExercicioCardio("   ", 30)


def test_cardio_duracao_invalida():
    with pytest.raises(ValueError):
        ExercicioCardio("Esteira", 0)
