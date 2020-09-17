from django import forms
from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseRedirect

from random import choice

from . import util
from . import markdown2


class NewPageForm(forms.Form):
    title = forms.CharField(label="title", widget=forms.TextInput(attrs={'class' : 'form-control col-md-8 col-lg-8'}))
    content = forms.CharField(label="content", widget=forms.Textarea(attrs={'class' : 'form-control col-md-8 col-lg-8', 'rows' : 10}))
    edit = forms.BooleanField(widget=forms.HiddenInput(), initial=False, required=False)

# Default page
def index(request):
    if request.method == "GET":
        return render(request, "encyclopedia/index.html", {
            "entries": util.list_entries(),
            "title": "All pages"
        })

# Pages' Urls
def wiki(request, name):
    if name.casefold() in util.list_entries():
        entry = markdown2.markdown(util.get_entry(name))
        return render(request, "encyclopedia/title.html", {
            "content": entry,
            "title": name,
            "edit": f"/edit/{name}"
        })
    else:
        return render(request, "encyclopedia/error.html")


# Search for pages
def search(request):

    # Take in the data the user submitted and save it as form
    form = request.GET.get('q', '')

    # If form an existing page, redirect to that page
    if(util.get_entry(form) is not None):
        return HttpResponseRedirect(reverse("wiki", kwargs={'name': form}))

    # Create a list of all the matches
    else:
        matches = []
        for entry in util.list_entries():
            if form.casefold() in entry:
                matches.append(entry)

        # If no match:
        if len(matches) == 0:
            return render(request, "encyclopedia/error.html")
        else:
            return render(request, "encyclopedia/index.html", {
                "entries": matches,
                "title": "Did you mean..."
            })

def new(request):

    if request.method == "POST":

        # Take in the data the user submitted and save it as form
        form = NewPageForm(request.POST)

        # Check if form data is valid (server-side)
        if form.is_valid():

            # Isolate the title and the content from the 'cleaned' version of form data
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]

            if form.fields["edit"] == False:

                # Isolate the title and the content from the 'cleaned' version of form data
                if title.casefold() in util.list_entries():
                    return render(request, "encyclopedia/error2.html", {
                        'link' : f"wiki/{title}"
                    })
            
            # Save entry
            util.save_entry(title,content)

            # Redirect user to list of pages
            return HttpResponseRedirect(reverse("wiki", kwargs={'name': title}))

        else:

            # If the form is invalid, re-render the page with existing information.
            return render(request, "encyclopedia/new.html", {
                "title": "Create a new page",
                "form": form,
                "alert": True
            })

    
    return render(request, "encyclopedia/new.html", {
        "title": "Create a new page",
        "form": NewPageForm(),
        "alert": False
    })

def edit(request, name):
    if request.method == "GET":
        form = NewPageForm()
        form.fields["title"].initial = name
        form.fields["content"].initial = util.get_entry(name)
        form.fields["edit"].initial = True
        return render(request, "encyclopedia/new.html", {
            "title": "Edit this page",
            "form": form,
            "alert": False
        })


def random(request):
    return HttpResponseRedirect(reverse("wiki", kwargs={'name': choice(util.list_entries())}))
