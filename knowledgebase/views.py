from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def index_view(request):
    file_tree = [
        {
            "type": "folder",
            "id": "folderIdeen",
            "name": "Ideen",
            "is_open": True,
            "children": [
                {
                    "type": "file",
                    "id": "fileWireframes",
                    "name": "App Wireframes",
                    "is_active": False
                },
                {
                    "type": "folder",
                    "id": "folder2027",
                    "name": "2027 Projekte",
                    "is_open": True,
                    "children": [
                        {
                            "type": "file",
                            "id": "fileProjektideen",
                            "name": "Projektideen 2027",
                            "is_active": True
                        },
                        {
                            "type": "folder",
                            "id": "folderArchive",
                            "name": "Archiv",
                            "is_open": False,
                            "children": [
                                {
                                    "type": "file",
                                    "id": "fileAlteKonzepte",
                                    "name": "Alte Konzepte",
                                    "is_active": False
                                }
                            ]
                        }
                    ]
                }
            ]
        },
        {
            "type": "file",
            "id": "fileScratchpad",
            "name": "Scratchpad",
            "is_active": False
        }
    ]

    context = {
        "file_tree": file_tree
    }
    return render(request, 'knowledge/index.html', context)

