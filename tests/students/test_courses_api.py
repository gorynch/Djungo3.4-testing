from random import randrange

import pytest
from django.urls import reverse
from model_bakery import baker
from rest_framework import status
from rest_framework.test import APIClient
from students.models import Student, Course


def get_model_fields(MyModel):
    return [field.name for field in MyModel._meta.get_fields()]


@pytest.fixture()
def client():
    return APIClient()


@pytest.fixture()
def student_factory():
    def s_factory(*args, **kwargs):
        return baker.make(Student, *args, **kwargs)
    return s_factory


@pytest.fixture()
def course_factory():
    def c_factory(*args, **kwargs):
        return baker.make(Course, *args, **kwargs)
    return c_factory


@pytest.mark.django_db
def test_first_course(client, course_factory):
    course = course_factory()
    url = reverse('courses-detail', kwargs={'pk': course.pk})
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data['id'] == course.id
    assert response.data['name'] == course.name
    assert list(response.data.keys()) == get_model_fields(Course)


@pytest.mark.django_db
def test_get_list_courses(client, course_factory):
    courses_quantity = 17
    course_factory(_quantity=courses_quantity)
    url = reverse('courses-list')
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == courses_quantity
    for c_data in response.data:
        assert list(c_data.keys()) == get_model_fields(Course)


@pytest.mark.django_db
def test_get_course_by_id(client, course_factory):
    courses_quantity = 7
    course = course_factory(_quantity=courses_quantity)
    filter_course_id = course[randrange(courses_quantity)].id

    url = reverse('courses-list')
    response = client.get(url, {'id': filter_course_id})

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]['id'] == filter_course_id


@pytest.mark.django_db
def test_get_course_by_name(client, course_factory):
    courses_quantity = 5
    courses = course_factory(_quantity=courses_quantity)
    filter_course_name = courses[randrange(courses_quantity)].name

    url = reverse('courses-list')
    response = client.get(url, {'name': filter_course_name})

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]['name'] == filter_course_name


@pytest.mark.django_db
def test_create_course(client):
    course_json_data = {'name': 'subject'}

    url = reverse('courses-list')
    response = client.post(url, data=course_json_data)
    data = client.get(url).json()

    assert response.status_code == status.HTTP_201_CREATED
    assert Course.objects.filter(name=course_json_data['name']).exists()
    assert len(data) == 1


@pytest.mark.django_db
def test_update_course(client, course_factory):
    course = course_factory()
    student = Student.objects.create(name='Oak')
    new_course_data = {'name': "New course name", 'students': [student.id]}

    url = reverse('courses-detail', kwargs={'pk': course.pk})
    response = client.patch(url, data=new_course_data)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()['name'] == new_course_data['name']


@pytest.mark.django_db
def test_delete_course(client, course_factory):

    course = course_factory()
    url = reverse('courses-detail', kwargs={'pk': course.pk})
    response = client.delete(url)

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Course.objects.filter(pk=course.pk).exists()
