# MPHelperFunctions.py

from .models import MPGame_contains_Quiztask

def get_next_turn(current_turn, player1, player2):
    # Wenn der aktuelle Spieler Player1 ist, setze den Turn auf Player2, sonst auf Player1
    if current_turn == player1:
        return player2
    else:
        return player1


def get_mp_game_stats(mp_game):
    tasks = MPGame_contains_Quiztask.objects.filter(game=mp_game)
    player1_correct = tasks.filter(player1_answer__correct=True).count()
    player2_correct = tasks.filter(player2_answer__correct=True).count()
    total_tasks = tasks.count()

    if total_tasks > 0:
        player1_percent = (player1_correct / total_tasks) * 100
        player2_percent = (player2_correct / total_tasks) * 100
    else:
        player1_percent = 0
        player2_percent = 0

    return {
        'player1_correct': player1_correct,  # Anzahl korrekter Antworten Spieler 1
        'player2_correct': player2_correct,  # Anzahl korrekter Antworten Spieler 2
        'total_questions': total_tasks,      # Gesamtanzahl der Fragen
        'player1_percent': player1_percent,  # Prozentwert Spieler 1
        'player2_percent': player2_percent   # Prozentwert Spieler 2
    }


def check_mp_game_completed(game):
    # Prüfen, ob alle Aufgaben abgeschlossen sind
    if MPGame_contains_Quiztask.objects.filter(game=game, completed=False).exists():
        return False
    game.completed = True
    game.save()
    return True

