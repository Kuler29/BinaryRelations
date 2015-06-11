from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from StudentSite.models import TaskModel, StudentTaskRel
from StudentSite.MathBackend.Task import Task
from StudentSite.MathBackend.OrderType import OrderType
import json
from django.utils import timezone


@login_required(login_url="student_site:login_registration")
def training(request):
    return render(request, 'StudentSite/training.html')

def training_with_difficulty(request, difficulty):
    user = request.user
    student = user.studentmodel
    diff = {'easy': 1, 'medium': 2, 'hard': 3}
    st_task_rel = student.studenttaskrel_set.filter(isTestTask=False, isCompleted=False, task__difficulty=diff[difficulty])

    if len(st_task_rel) == 0:
        task = TaskModel.get_training_task_with_difficulty(difficulty)
        task_obj = Task.from_string(task.str_repr)
        st_task_rel = StudentTaskRel(task=task, student=student, isTestTask=False, dateStarted=timezone.now())
        st_task_rel.save()
    else:
        st_task_rel = st_task_rel[0]
        task_obj = Task.from_string(st_task_rel.task.str_repr)

    context = {'task': task_obj, 'relation_id': st_task_rel.id, 'is_control': False}

    if st_task_rel.matrix_completed:
        context['result'] = True

    context['partial_solve'] = json.dumps(st_task_rel.partial_solve_matrix)

    return render(request, 'StudentSite/site_pages/matrix.html', context)

def check_matrix(request):
    # Получаем объект отношения из базы данных с id, соответствующим тому,
    # что было передано пользователем в POST запросе
    st_task_rel = StudentTaskRel.objects.get(pk=request.POST['relation_id'])
    # Создаем объект задания из его строкового представления
    task = st_task_rel.task
    task_obj = Task.from_string(task.str_repr)

    # Проверяем, имеет ли записать задания в базе данных решение
    if task.answer_matrix is None:
        # Если нет, то "просим" объект задания сформировать это решение и сохраняем его в базу
        task.answer_matrix = task_obj.solve_string()
        task.save()

    # Получаем результат выполнения, отправленный пользователем и сохраняем его в базе
    st_task_rel.partial_solve_matrix = request.POST['answers_string']
    st_task_rel.save()

    # Сверяем ответ пользователя с верным решением
    if st_task_rel.partial_solve_matrix == task.answer_matrix:
        # Если они совпадают, то переменной с результатом, которая попадет в контекст
        # присваиваем значение True
        result = True
        # В записи отношения отмечаем, что пользователь справился с матрицей и сохраняем изменения в базе данных
        st_task_rel.matrix_completed = True
        st_task_rel.save()
    else:
        st_task_rel.numberOfAttempts += 1
        st_task_rel.save()
        # Если не совпадают, то переменной с результатом присваиваем False
        result = False

    # Формируем контекст, который будет передан шаблону для формирования HTML кода

    context = {
        # Под ключем task передаем объект задания. Будет использоваться для
        # заполнения шапки матрицы правильными элементами, а так же для формирования
        # описания задачи
        'task': task_obj,
        # Справился ли пользователем с задачей
        'result': result,
        # id отношения между студентом и заданием
        'relation_id': st_task_rel.id,
        # Так как страницы для режима контроля и тренировки практически идентичны, за
        # исключением подсветки неверных решений, для них используется один и тот же шаблон,
        # и с помощью переменной контекста is_control происходит разграничение контента, который
        # должен быть представлен только в одном из режимов
        'is_control': False,
        # JSON объект с частичным решением задачи, с которого пользователь будет продолжать выполнение
        'partial_solve': json.dumps(st_task_rel.partial_solve_matrix),
        # JSON объект с правильными решением задачи.
        # Передается в JavaScript функцию, которая подсветит элементы матрицы с неверным содержанием
        'correct_solve': json.dumps(task.answer_matrix)
    }
    # Возвращаем результат выполнения render() с запросом пользователя, адресом нужного шаблона и контекстом
    return render(request, 'StudentSite/site_pages/matrix.html', context)

def properties(request):
    st_task_rel = StudentTaskRel.objects.get(pk=request.POST['relation_id'])

    context = {"relation_id": st_task_rel.id,
               "result": True if st_task_rel.properties_completed else None,
               "task": Task.from_string(st_task_rel.task.str_repr),
               "is_control": False,
               "partial_solve": json.dumps(st_task_rel.partial_solve_properties),
               "matrix_solve": json.dumps(st_task_rel.task.answer_matrix)
               }

    return render(request, 'StudentSite/site_pages/properties.html', context)

def check_properties(request):
    st_task_rel = StudentTaskRel.objects.get(pk=request.POST['relation_id'])
    task_obj = Task.from_string(st_task_rel.task.str_repr)

    st_task_rel.partial_solve_properties = request.POST['answers_string']
    st_task_rel.save()

    if st_task_rel.task.answer_properties is None:
        st_task_rel.task.answer_properties = task_obj.solve_properties()
        st_task_rel.task.save()

    if st_task_rel.partial_solve_properties == st_task_rel.task.answer_properties:
        result = True
        st_task_rel.properties_completed = True
        st_task_rel.save()
    else:
        st_task_rel.numberOfAttempts += 1
        st_task_rel.save()
        result = False

    context = {"relation_id": st_task_rel.id,
               "result": result,
               "task": task_obj,
               "is_control": False,
               "partial_solve": json.dumps(st_task_rel.partial_solve_properties),
               "correct_solve": json.dumps(st_task_rel.task.answer_properties),
               "matrix_solve": json.dumps(st_task_rel.task.answer_matrix)
               }

    return render(request, 'StudentSite/site_pages/properties.html', context)


def warshalls(request):
    st_task_rel = StudentTaskRel.objects.get(pk=request.POST['relation_id'])

    context = {"relation_id": st_task_rel.id,
               "result": True if st_task_rel.is_warshall_completed else None,
               "task": Task.from_string(st_task_rel.task.str_repr),
               "is_control": False,
               "partial_solve": json.dumps(st_task_rel.partial_solve_warshalls),
               "matrix_solve": json.dumps(st_task_rel.task.answer_matrix)
               }

    return render(request, 'StudentSite/site_pages/warshalls.html', context)

def check_warshalls(request):
    st_task_rel = StudentTaskRel.objects.get(pk=request.POST['relation_id'])

    st_task_rel.partial_solve_warshalls = request.POST['answers_string']
    task_obj = Task.from_string(st_task_rel.task.str_repr)
    st_task_rel.save()

    if st_task_rel.task.answer_warshalls is None:
        st_task_rel.task.answer_warshalls = task_obj.generate_warshalls_strings()
        st_task_rel.task.save()

    result = st_task_rel.task.answer_warshalls == st_task_rel.partial_solve_warshalls

    if result:
        st_task_rel.is_warshall_completed = True
        if task_obj.is_of_order() == OrderType.not_of_order:
            st_task_rel.isCompleted = True
            st_task_rel.save()
            from .views import result
            return result(request)
        st_task_rel.save()
    else:
        st_task_rel.numberOfAttempts += 1
        st_task_rel.save()

    context = {"relation_id": st_task_rel.id,
               "result": result,
               "task": task_obj,
               "is_control": False,
               "partial_solve": json.dumps(st_task_rel.partial_solve_warshalls),
               "matrix_solve": json.dumps(st_task_rel.task.answer_matrix),
               "correct_warshalls": json.dumps(st_task_rel.task.answer_warshalls)}

    return render(request, 'StudentSite/site_pages/warshalls.html', context)

def topological(request):
    st_task_rel = StudentTaskRel.objects.get(pk=request.POST['relation_id'])

    context = {"relation_id": st_task_rel.id,
               "result": True if st_task_rel.is_topological_sort_completed else None,
               "task": Task.from_string(st_task_rel.task.str_repr),
               "is_control": False,
               "partial_solve": json.dumps(st_task_rel.partial_solve_warshalls),
               "matrix_solve": json.dumps(st_task_rel.task.answer_matrix)
               }

    return render(request, 'StudentSite/site_pages/warshalls.html', context)

def check_topological(request):
    st_task_rel = StudentTaskRel.objects.get(pk=request.POST['relation_id'])

    st_task_rel.partial_solve_topological_sort = request.POST['users_solve']
    task_obj = Task.from_string(st_task_rel.partial_solve_topological_sort)

    context = {
        "relation_id": st_task_rel.id,
        "result": False,
        "task": task_obj,
        "is_control": False,
        "partial_solve": json.dumps(st_task_rel.partial_solve_topological_sort),
        "matrix_solve": json.dumps(st_task_rel.task.answer_matrix)
    }

    return render(request, 'StudentSite/site_pages/topological.html', context)