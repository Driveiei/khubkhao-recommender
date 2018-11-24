from django.views.generic import TemplateView
from django.shortcuts import render
from django.http import HttpResponse
from khubkhaoapp.models import Category,EthnicFood, Food
from django.db.models import Q
from enum import Enum

class HomeView(TemplateView):
    template_name = 'registration/login.html'


class Rate(Enum):
    ONE = 20
    TWO = 40
    THREE = 60
    FOUR = 80
    FIVE = 100

def vote_value(raw_number):
    if(raw_number == "ONE") :
        return Rate.ONE
    elif(raw_number == "TWO") :
        return Rate.TWO
    elif(raw_number == "THREE") :
        return Rate.THREE
    elif(raw_number == "FOUR") :
        return Rate.FOUR
    else :
        return Rate.FIVE


class IndexView(TemplateView):
    template_name = 'khubkhaoapp/index.html'
    def get_context_data(self,*args,**kwargs):
        context = super(IndexView,self).get_context_data(*args, **kwargs)
        unsorted_results = Food.objects.all()
        food_list = sorted(unsorted_results, key = lambda food: food.compute_total_rate(), reverse=True)[:25]
        category_list = Category.objects.all()
        ethnic_list = EthnicFood.objects.all()
        context = {
            'food_list': food_list,
            'category_list': category_list,
            'ethnic_list': ethnic_list,
        }
        return context


def filter_ethnic(ethnic):
    return EthnicFood.objects.filter(id__in=ethnic)

def filter_category(category):
    return Category.objects.filter(id__in=category)

def filter_food(selected_ethnic,selected_category):
    if not selected_category.exists() and not selected_ethnic.exists():
        return Food.objects.all()
    elif not selected_category.exists() or not selected_ethnic.exists():
        return Food.objects.filter(Q(ethnic_food_name__in=selected_ethnic) | Q(
            category__in=selected_category)).distinct()
    return Food.objects.filter(ethnic_food_name__in=selected_ethnic).filter(
        category__in=selected_category).distinct()

def sort_food(unsort_food):
    return sorted(unsort_food, key = lambda food: food.compute_total_rate(), reverse=True)[:25]

def IndexResultView(request):
    if request.method == "POST":
        my_ethnic = request.POST.getlist('ethnic_name')
        my_category = request.POST.getlist('category_name')
    selected_ethnic = filter_ethnic(my_ethnic)
    selected_category = filter_category(my_category)
    food_list = filter_food(selected_ethnic,selected_category)
    food_list = sort_food(food_list)
    category_list = Category.objects.all()
    ethnic_list = EthnicFood.objects.all()
    context = {
        'food_list': food_list,
        'category_list': category_list,
        'ethnic_list': ethnic_list,
    }
    return render(request, 'khubkhaoapp/index.html', context)

def vote_food(pk_food,vote):
    vote_scores = vote_value(vote).value
    food = Food.objects.get(pk=pk_food)
    food.add_user_count()
    food.set_user_rate(vote_scores)
    print(vote_scores)
    food.save()

def IndexVoteView(request):
    if request.method == "POST":
        my_vote = request.POST.get('rate_star')
    pk_and_vote = my_vote.split(',')
    vote_food(pk_and_vote[0],pk_and_vote[1])
    
    food_list = Food.objects.all()
    food_list = sort_food(food_list)
    category_list = Category.objects.all()
    ethnic_list = EthnicFood.objects.all()
    context = {
        'food_list': food_list,
        'category_list': category_list,
        'ethnic_list': ethnic_list,
    }
    return render(request,'khubkhaoapp/index.html', context)