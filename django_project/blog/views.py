from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Post
from .forms import CreateUserForm
from .decorators import unauthenticated_user, allowed_users
import boto3
import json
from boto3.dynamodb.conditions import Key
from datetime import date
client=boto3.resource('dynamodb',region_name='us-east-2')

manager_table = client.Table('Manager')
lead_ids = {'Anand':'0003','Jimmy':'0006'}
result = manager_table.scan()
# print(result)
data = result['Items']
sr_numbers=[]
while 'LastEvaluatedKey' in result:
    result = manager_table.scan(ExclusiveStartKey=result['LastEvaluatedKey'])
    data.extend(result['Items'])
for i in data:
    sr_numbers.append(int(i['sr_no']))

sr_numbers.sort()
current_srno = sr_numbers[-1]
lead_ids = {'Anand':'0003','Jimmy':'0006'}

# def push_to_db(id,project_name,description,deadline,lead_assigned):
#     global current_srno
#     current_srno += 1
#
#     lead_id = lead_ids[lead_assigned]
#     manager_table.put_item(
#     # Item={
#     # 		emp_id:'9',
#     # 		'Project name':"Truck2222",
#     # 		'deadline':'15435',
#     # 		'description':'B33hdhdhdhhffhdhfdh3uild a truck from start'
#
#     # 	}
#     # 	)
#     Item={
#         'sr_no':current_srno,
#         'id': id,
#         'Project_name': project_name,
#         'description': description,
#         'deadline': deadline,
#         'issue_date': str(date.today()),
#         'lead_assigned': lead_assigned,
#         'Lead_assigned_id':lead_id,
#
#     })
#     print('Done')


# push_operation()
####################################xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx####################
data_list = []
for i in data:
    idno = i['id']
    projectname = i['Project_name']
    description = i['description']
    dline = i['deadline']
    lead = i['lead_assigned']
    date_posted = i['issue_date']

    x = {
        'idno': idno,
        'date_posted': date_posted,
        'projectname': projectname,
        'description': description,
        'dline': dline,
        'lead': lead,
        # 'username': username,

    }
    data_list.append(x)
############################XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

######################################################################################################
posts = [
    {
        'author': 'CoreyMS',
        'title': 'Blog Post 1',
        'content': 'First post content',
        'date_posted': 'August 27, 2018'
    },
    {
        'author': 'Jane Doe',
        'title': 'Blog Post 2',
        'content': 'Second post content',
        'date_posted': 'August 28, 2018'
    }
]
@login_required(login_url='blog-login')
@allowed_users(allowed_roles=['Manager'])
def home(request):
    context = {
        'posts':posts
        # 'posts': Post.objects.all()
    }
    return render(request, 'blog/home.html', context)

class PostListView(ListView):

    model = Post
    template_name = 'blog/home.html'
    context_object_name = 'posts'
    order = ['-date_posted']

class PostDetailView(DetailView):
    model = Post


def push_to_db(id,project_name,description,deadline,lead_assigned):
    global current_srno
    current_srno += 1

    lead_id = lead_ids[lead_assigned]
    manager_table.put_item(

    Item={
        'sr_no':str(current_srno),
        'id': id,
        'Project_name': project_name,
        'description': description,
        'deadline': deadline,
        'issue_date': str(date.today()),
        'lead_assigned': lead_assigned,
        'Lead_assigned_id':lead_id,

    })
    print('Done')
class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['id_number','title', 'content','deadline','lead_assigned']
    def form_valid(self, form):
        form.instance.author = self.request.user
        project_title = form.instance.title
        project_description = form.instance.content
        # date_posted = form.instance.date_posted
        deadline= form.instance.deadline
        lead_assigned= form.instance.lead_assigned
        id_number = form.instance.id_number

        push_to_db(id_number, project_title, project_description, deadline, lead_assigned)
        return redirect('manager')
        return super().form_valid(form)

class PostUpdateView(LoginRequiredMixin,UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['title', 'content']
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False

class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url ='/'
    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False
def find_lead_id(username):
    for i in lead_ids:
        if i==username:
            return i[username]
        else:
            return 'invalid'
@login_required(login_url='blog-login')
def about(request):
    return render(request, 'blog/about.html', {'title': 'About'})

def tasks_from_manager(lead_id):
    projects_for_lead=[]
    result = manager_table.scan()
    # print(result)
    data = result['Items']

    while 'LastEvaluatedKey' in result:
        result = manager_table.scan(ExclusiveStartKey=result['LastEvaluatedKey'])
        data.extend(result['Items'])
    for i in data:
        if i['Lead_assigned_id'] == lead_id:
            projects_for_lead.append(i['Project_name'])

    if len(projects_for_lead) == 0:
        return ['No projects for you']
    else:
        return projects_for_lead
@login_required(login_url='blog-login')
def lead(request):
    username = request.POST.get('username')
    print("userrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr",username)
    id1 = find_lead_id(username)
    project_for_lead=tasks_from_manager('0006')
    print("hhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh",project_for_lead)
    return render(request, 'blog/lead.html', {'available_projects':project_for_lead})

@login_required(login_url='blog-login')
def resource(request):
    return render(request, 'blog/resource.html', {'title': 'Resource'})

@login_required(login_url='blog-login')
def Welcome(request):
    return render(request, 'blog/welcome.html', {'title': 'Welcome'})


@unauthenticated_user
def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username = username, password = password)
        if user is not  None:
            login(request, user)
            group = request.user.groups.all()[0].name
            if group == 'Manager':
                return redirect('manager')
            elif group == 'Project Lead':
                return redirect('blog-lead')
            else:
                return redirect('blog-resource')
        else: 
            messages.info(request, 'Username or Password is Incorrect')

    return render(request, 'blog/login.html', {'title': 'Login'})

@unauthenticated_user
def registerPage(request):
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            user = form.cleaned_data.get('username')
            messages.success(request, 'Account Created:' + user)
            return redirect('blog-login')

    context = {'form' : form}
    return render(request, 'blog/register.html', context)

def profile(request):
    return render(request, 'blog/profile.html', {'title': 'Profile'})

def logoutUser(request):
    logout(request)
    return redirect('blog-login')
# def get_manager_id(username):
#     if username in user_list():

def manager(request):
    manager_table = client.Table('Manager')
    result = manager_table.scan()
    data = result['Items']
    while 'LastEvaluatedKey' in result:
        result = manager_table.scan(ExclusiveStartKey=result['LastEvaluatedKey'])
        data.extend(result['Items'])
    data_list=[]
    username = request.POST.get('username')
    print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$",username)
    index_test=0
    index_list=[]
    for i in data:
        idno = i['id']
        projectname = i['Project_name']
        description = i['description']
        dline = i['deadline']
        lead=i['lead_assigned']
        date_posted = i['issue_date']
        x={
            'idno':idno,
            'date_posted':date_posted,
            'projectname':projectname,
            'description':description,
            'dline':dline,
            'lead':lead,

            # 'username':username,

        }
        data_list.append(x)

    for i in range(0,len(data_list)):
        index_list.append(1)



    return render(request, 'blog/manager.html',{'data_list':data_list,'sr_no':current_srno, 'index_list':index_list})


    # def push_operation():
    #     idno = input("Enter you're ID number")
    #     projectname = input('Enter the name of the project')
    #     descrip = input("Describe the project")
    #     dline = input('Enter the deadline')
    #     lead = input('Enter the lead to be assigned for this project')
    #     push_to_db(idno, projectname, descrip, dline, lead)
    # return render(request, 'blog/manager.html')
# @login_required
# def profile(request):
#     if request.method == 'POST':
#         u_form  = UserUpdateForm(request.POST, instance=request.user)
#         p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
#         if u_form.is_valid() and p_form.is_valid():
#             u_form.save()
#             p_form.save()
#             messages.success(request, f'Your Account has been Updated')
#             return redirect('profile')
#     else:
#         u_form  = UserUpdateForm(instance=request.user)
#         p_form = ProfileUpdateForm(instance=request.user.profile)
        
#     context = {
#         'u_form' : u_form,
#         'p_form' : p_form
#     }
#     return render(request, 'blog/profile.html', context)
