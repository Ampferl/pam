import json
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .models import KnowledgeItem


def build_tree_recursive(item, active_item_id):
    children = item.children.all()
    node = {
        "id": item.id,
        "name": item.name,
        "type": item.item_type,
        "is_open": True,
        "is_active": (item.id == active_item_id),
        "children": [build_tree_recursive(child, active_item_id) for child in children] if item.item_type == 'folder' else []
    }
    return node


def flatten_folders(nodes, depth=0):
    folders = []
    for node in nodes:
        if node["type"] == "folder":
            folders.append({
                "id": node["id"],
                "label": ("— " * depth) + node["name"],
            })
            folders.extend(flatten_folders(node["children"], depth + 1))
    return folders


@login_required
def index_view(request, item_id=None):
    items = KnowledgeItem.objects.filter()

    active_item = None
    if item_id:
        active_item = get_object_or_404(KnowledgeItem, id=item_id)
    else:
        active_item = items.filter(item_type='file').first()

    active_id = active_item.id if active_item else None
    root_items = items.filter(parent__isnull=True)
    file_tree = [build_tree_recursive(item, active_id) for item in root_items]

    context = {
        "file_tree": file_tree,
        "active_item": active_item,
        "all_folders": flatten_folders(file_tree),
    }
    return render(request, 'knowledge/index.html', context)


@login_required
def item_create_view(request):
    item_type = request.POST.get('item_type', 'file')
    parent_id = request.POST.get('parent_id')
    name = request.POST.get('name', 'Neue Notiz')

    parent = None
    if parent_id:
        parent = get_object_or_404(KnowledgeItem, id=parent_id)

    item = KnowledgeItem.objects.create(
        name=name,
        item_type=item_type,
        parent=parent,
        content="" if item_type == 'file' else ""
    )

    if item_type == 'file':
        return redirect('knowledge:note_detail', item_id=item.id)
    return redirect('knowledge:overview')


@login_required
def item_update_view(request, item_id):
    item = get_object_or_404(KnowledgeItem, id=item_id)

    item.name = request.POST.get('name', item.name)
    if item.item_type == 'file':
        item.content = request.POST.get('content', '')

    item.save()
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({"status": "success", "name": item.name})
    return redirect('knowledge:note_detail', item_id=item.id)


@login_required
@require_POST
def item_rename_view(request, item_id):
    item = get_object_or_404(KnowledgeItem, id=item_id)
    data = json.loads(request.body)
    new_name = data.get('name', '').strip()
    if new_name:
        item.name = new_name
        item.save()
        return JsonResponse({"status": "success", "new_name": item.name})
    return JsonResponse({"status": "error", "message": "Ungültiger Name"}, status=400)

@login_required
@require_POST
def item_move_view(request, item_id):
    item = get_object_or_404(KnowledgeItem, id=item_id)
    data = json.loads(request.body)
    new_parent_id = data.get('parent_id')

    if new_parent_id:
        new_parent = get_object_or_404(KnowledgeItem, id=new_parent_id, item_type='folder')
        if item.id == new_parent.id:
            return JsonResponse({"status": "error", "message": "Kann sich nicht selbst verschachteln"}, status=400)
        item.parent = new_parent
    else:
        item.parent = None

    item.save()
    return JsonResponse({"status": "success"})


@login_required
def item_delete_view(request, item_id):
    item = get_object_or_404(KnowledgeItem, id=item_id)
    parent_id = item.parent.id if item.parent else None
    item.delete()

    return redirect('knowledge:overview')

