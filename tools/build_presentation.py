"""Build the editable coursework deck and matching PDF from vector slide layouts.

Usage: python3 tools/build_presentation.py
PDF generation requires ReportLab; PowerPoint packaging uses the standard library.
"""
from pathlib import Path
from dataclasses import dataclass, field
from xml.sax.saxutils import escape
import math
import zipfile

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs'
W, H = 960, 540
DARK, CARD, LINE = '0C1724', '142635', '2C4253'
WHITE, MUTED, TEAL, GOLD = 'F0F5F7', 'A6B9C9', '72DFC4', 'F3C779'
PAPER, INK, SOFT, GREEN = 'F4F1E9', '172E3D', '5A6F7B', '147D70'
TEAM = 'Amirzhanuly Abay  /  Shikhiyev Alikhan'

@dataclass
class Slide:
    title: str
    section: str
    light: bool = False
    notes: str = ''
    minutes: str = '1 min'
    shapes: list = field(default_factory=list)

    @property
    def fg(self): return INK if self.light else WHITE
    @property
    def muted(self): return SOFT if self.light else MUTED
    @property
    def accent(self): return GREEN if self.light else TEAL
    @property
    def bg(self): return PAPER if self.light else DARK

    def rect(self, x, y, w, h, fill, stroke=None, radius=False):
        self.shapes.append(dict(kind='rect', x=x, y=y, w=w, h=h, fill=fill, stroke=stroke, radius=radius))

    def circle(self, x, y, diameter, fill, stroke=None):
        self.shapes.append(dict(kind='circle', x=x, y=y, w=diameter, h=diameter, fill=fill, stroke=stroke))

    def line(self, x1, y1, x2, y2, color=None, width=1.5, arrow=False):
        self.shapes.append(dict(kind='line', x=x1, y=y1, x2=x2, y2=y2, color=color or self.accent, width=width, arrow=arrow))

    def text(self, x, y, w, content, size=18, color=None, bold=False, align='l', leading=None):
        lines = str(content).split('\n')
        self.shapes.append(dict(kind='text', x=x, y=y, w=w, h=len(lines)*(leading or size*1.22)+4,
            content=lines, size=size, color=color or self.fg, bold=bold, align=align, leading=leading or size*1.22))

    def heading(self, eyebrow, title):
        self.text(56, 34, 848, eyebrow, 10, self.accent, True)
        self.text(56, 64, 848, title, 34, bold=True)

    def card(self, x, y, w, h, number, title, body):
        self.rect(x,y,w,h,'FFFFFF' if self.light else CARD, 'D9DED9' if self.light else LINE, True)
        self.text(x+20,y+19,w-40,number,11,self.accent,True)
        self.text(x+20,y+48,w-40,title,21,bold=True)
        self.text(x+20,y+85,w-40,body,15,self.muted)

slides = []
def new(title, section, light=False, minutes='1 min', notes=''):
    s=Slide(title,section,light,notes,minutes)
    slides.append(s)
    return s

s=new('Memory Palace', 'PROJECT & TEAM', minutes='45 sec', notes='''Good afternoon. We are Amirzhanuly Abay and Shikhiyev Alikhan. Our project is Memory Palace — Knowledge Atlas, a personal knowledge workspace built with C#, .NET 10, and Blazor Server.
The project starts from a simple observation: collecting definitions is easier than explaining how those definitions connect. We wanted a small application where a student can capture an idea, describe a relationship, and follow a chain into another subject.
We will show the user workflow, explain the architecture and integrity rules, walk through the path-finding algorithm, and finish with a live demonstration and the verification results. The scope is a local personal workspace rather than a multi-user cloud service.''')
s.text(56,49,600,'C# / .NET CROSS-PLATFORM DEVELOPMENT',11,TEAL,True)
s.text(56,126,510,'Memory\nPalace',66,bold=True,leading=69)
s.text(59,284,460,'KNOWLEDGE ATLAS',18,TEAL,True)
s.text(59,331,460,'Capture ideas. Connect meaning.\nDiscover a path between them.',21,MUTED)
s.line(60,407,434,407,LINE)
s.text(59,427,480,'Amirzhanuly Abay',15,bold=True)
s.text(59,451,480,'Shikhiyev Alikhan',15,bold=True)
pts=[(686,140,TEAL),(824,213,GOLD),(681,292,'92ABFF'),(835,365,TEAL),(573,384,GOLD)]
for a,b in [(0,1),(0,2),(1,2),(1,3),(2,3),(2,4)]:
    s.line(pts[a][0],pts[a][1],pts[b][0],pts[b][1],LINE,2)
for i,(x,y,c) in enumerate(pts):
    s.circle(x-19,y-19,38,CARD,c)
    s.circle(x-5,y-5,10,c)
for x,y,t in [(643,102,'CONCEPT'),(797,174,'RELATION'),(631,325,'DISCOVERY')]:s.text(x,y,145,t,9,MUTED,True)

s=new('The problem and the goal', 'AIM & OBJECTIVES', minutes='75 sec', notes='''The intended audience is students organizing material across subjects. Ordinary notes can store useful definitions, but related ideas are often separated by files, folders, or courses. A student may know each term without being able to explain the relationship between them.
Our aim is to make those relationships visible and searchable. The three core objectives are capture, connect, and discover. Capture means validated concepts with descriptions and categories. Connect means directed, typed relationships with a short note explaining the link. Discover means search, filtering, and a shortest chain between two concepts.
Persistence and backup support all three objectives. The practical value is an inspectable study atlas; we have not conducted a study claiming improved memory or higher grades. For the demonstration, the example combines learning techniques, graph theory, and the technologies used to build the application.''')
s.heading('02 / AIM & OBJECTIVES','From isolated notes to connected ideas')
s.text(56,129,830,'A personal study atlas for understanding relationships across subjects.',19,s.muted)
s.card(56,187,270,228,'01 / CAPTURE','Keep ideas concise','Concepts, descriptions,\ncategories, and persistent\nlocal storage.')
s.card(345,187,270,228,'02 / CONNECT','Explain each link','Directed links with a type\nand a note: what connects\nthese two ideas?')
s.card(634,187,270,228,'03 / DISCOVER','Follow a chain','Search, filter, and find\na shortest route between\nareas of knowledge.')
s.text(58,449,840,'DESIGN GOAL   Make connections explainable, not just visible.',14,TEAL,True)

s=new('Existing approaches', 'RELEVANCE & COMPARISON', True, notes='''We compared approaches rather than trying to reproduce every feature of a large commercial tool. Files and linear notes are simple and portable, and they work well for long-form content. Wiki-style links improve navigation, but a relationship such as supports or contradicts still needs a convention. General graph systems offer flexible modeling and more powerful queries, with more setup and a steeper learning curve.
Memory Palace narrows the problem to concise concepts, five relationship types, and unweighted path discovery. It combines a spatial view with a conventional searchable library, so users do not have to rely on the graph for every action.
This is the project's relevance and its main design trade-off: fewer features, but a focused workflow that can be implemented, tested, and explained within the course scope. It is not a claim that a small coursework application replaces all note-taking or graph-database products.''')
s.heading('03 / EXISTING APPROACHES','A focused place between notes and graphs')
rows=[('Linear notes','Fast capture; long-form writing','Connections remain implicit.'),('Wiki-style links','Simple navigation between pages','Typed meaning needs a convention.'),('General graph systems','Flexible models and queries','More setup and learning overhead.'),('Memory Palace','Concepts + typed links + discovery','Focused on a personal study atlas.')]
for i,(a,b,c) in enumerate(rows):
    y=143+i*77
    s.rect(56,y,848,66,'E2EDE6' if i==3 else 'FFFFFF',None,True)
    s.text(74,y+12,210,a,18,GREEN if i==3 else INK,True)
    s.text(298,y+11,580,b,17,bold=i==3)
    s.text(298,y+35,580,c,14,SOFT)

s=new('Technology choices', 'STACK & TRADE-OFFS', minutes='90 sec', notes='''The application targets .NET 10 and uses Blazor Server for UI event handling. That lets us write both UI workflows and business logic in C#, with direct server-side access to the service layer. It avoids a separate REST API for this local scope, but the browser needs a connection to the running server.
Blazor WebAssembly would move UI execution into the browser. The trade-offs include downloading the browser runtime and introducing a separate boundary for data access. Neither hosting model is universally better; the choice follows the deployment and learning goals.
SQLite is a file-based database with no separate server installation. It is convenient for a portable personal workspace, while an external relational database is a better fit for multiple application servers or heavier concurrent writes. EF Core handles mapping and transactions. We chose SVG and CSS for the graph rather than adding a separate graph-rendering framework.''')
s.heading('04 / TECHNOLOGY CHOICES','A small stack with explicit trade-offs')
s.text(56,129,848,'C#  /  .NET 10  /  Blazor Server  /  EF Core  /  SQLite',17,TEAL,True)
headers=[(75,'OPTION'),(284,'STRENGTH'),(608,'TRADE-OFF')]
for x,t in headers:s.text(x,180,280,t,10,MUTED,True)
tech=[('Blazor Server','C# UI + direct service access','Persistent server connection'),('Blazor WebAssembly','UI executes in the browser','Runtime download + API boundary'),('SQLite','One file; no DB server setup','Limited concurrent writes'),('External relational DB','Multiple servers; heavier writes','More deployment and operations')]
for i,(a,b,c) in enumerate(tech):
    y=209+i*56
    s.line(56,y-8,904,y-8,LINE,1)
    s.text(75,y+3,205,a,16,TEAL if i in(0,2) else WHITE,True)
    s.text(284,y+3,305,b,15)
    s.text(608,y+3,290,c,14,MUTED)
s.text(58,460,840,'CHOSEN FOR THIS SCOPE   Blazor Server + SQLite',13,TEAL,True)

s=new('The workspace', 'WORKFLOW & METHODOLOGY', minutes='75 sec', notes='''This is an interface schematic, not a screenshot of a measured browser session. The main layout puts the current workspace in the center and selected-concept details on the right. A narrow navigation rail switches between the spatial map and the library. Search and category controls narrow the same underlying concept set.
The normal workflow is to create a concept, connect it, and explore the resulting relationships. The detail panel keeps the definition and connection notes beside the graph, rather than requiring navigation away. The library is important as an alternative for users who prefer text-based browsing or have a larger collection.
The development method followed four increments: establish the model and integrity rules, complete workflows, verify the core and service behavior, and prepare delivery materials. The page coordinates actions, but reusable editor, modal, graph, and detail components each have narrower responsibilities.''')
s.heading('05 / WORKFLOW & METHODOLOGY','One workspace, two ways to explore')
s.rect(56,136,848,299,CARD,LINE,True)
s.rect(56,136,40,299,'0A1420')
s.text(66,154,26,'M',18,TEAL,True)
s.text(67,202,24,'01\n\n02',11,MUTED)
s.text(116,154,495,'Knowledge Atlas',19,bold=True)
s.rect(116,190,480,28,DARK,LINE,True)
s.text(128,197,350,'Search concepts...    /    All categories',10,MUTED)
s.rect(116,230,480,181,DARK,None,True)
mini=[(198,275),(352,258),(475,318),(296,367)]
for a,b in[(0,1),(1,2),(0,3),(1,3)]:s.line(*mini[a],*mini[b],LINE,2)
for (x,y),label in zip(mini,['Active Recall','Memory Palace','SQLite','Graph Theory']):
    s.circle(x-6,y-6,12,TEAL)
    s.text(x-57,y+12,114,label,10,WHITE,align='ctr')
s.rect(619,154,266,257,DARK,LINE,True)
s.text(639,173,220,'CONCEPT EXPLORER',9,TEAL,True)
s.text(639,203,220,'Memory Palace',21,bold=True)
s.text(639,244,220,'A personal atlas of concepts\nand meaningful relationships.',12,MUTED)
s.line(639,290,862,290,LINE)
s.text(639,306,220,'CONNECTED IDEAS',9,TEAL,True)
s.text(639,332,220,'Active Recall    /    Supports\nGraph Theory  /    Explains',12,MUTED,leading=24)
s.text(56,455,848,'METHOD   Model → Workflows → Verification → Delivery',14,TEAL,True)
s.text(721,421,168,'Interface schematic',9,MUTED,align='r')

s=new('Architecture', 'SYSTEM DESIGN', True, minutes='2 min', notes='''The browser communicates with a Blazor Server circuit. Index coordinates user workflows and feedback. AtlasState holds the current snapshot, filters, counts, and selected concept. Components depend on IConceptService rather than on the database context; ConceptService owns validation, transactions, and backup workflows.
State is scoped to one circuit, so independent tabs keep separate selections and search terms. The database itself is shared. A refresh explicitly reloads changes from another tab; there is no custom broadcast service.
A central design choice is IDbContextFactory. A Blazor circuit can live much longer than one HTTP request, and handlers may overlap. EF Core contexts are not thread-safe, so every service operation creates and disposes a short-lived context. The graph algorithm is independent of UI and persistence, making it straightforward to test.
Continuous map gestures now render locally in the browser. Only a completed node move updates the component state. This avoids a server round trip for every pointer movement while preserving the concept's position across component renders.''')
s.heading('06 / ARCHITECTURE','Clear responsibilities, short-lived contexts')
blocks=[(56,'BROWSER','Razor components'),(276,'APPLICATION','Index + AtlasState'),(496,'SERVICE','IConceptService'),(716,'PERSISTENCE','EF Core + SQLite')]
for x,tag,title in blocks:
    s.rect(x,174,188,111,'FFFFFF','D2DDD5',True)
    s.text(x+15,192,163,tag,9,GREEN,True)
    s.text(x+15,222,163,title,16,INK,True)
for x in [250,470,690]:s.line(x,229,x+18,229,GREEN,2,True)
s.card(56,326,410,128,'STATE LIFETIME','One circuit, one workspace','Selection and filters stay local to the tab.')
s.card(494,326,410,128,'DATABASE LIFETIME','One operation, one context','IDbContextFactory avoids shared-context access.')

s=new('Data integrity', 'MODEL & TRANSACTIONS', minutes='90 sec', notes='''The domain model has two entities. Concept contains an ID, title, description, category, and creation/update timestamps. Connection contains its own ID, a source concept, a target concept, a relationship type, and an optional note.
The ordered source and target pair has a unique database index. This prevents a duplicate A-to-B relationship, while allowing B-to-A as a distinct relationship. The service rejects self-links, missing endpoints, undefined relation values, and invalid text lengths. Titles are trimmed, normalized, and checked without case sensitivity in the service transaction. Title uniqueness is not a separate database constraint.
Deleting a concept first removes both incoming and outgoing relationships, then the concept, in one transaction. This matters because the target-side foreign key restricts deletion.
Restore validates the complete backup before writing and requires an empty atlas. One transaction commits the validated set. Flat records avoid cycles from EF navigation properties. The goal is predictable failure without leaving dangling edges or a half-restored workspace.''')
s.heading('07 / MODEL & TRANSACTIONS','Two entities. Explicit integrity rules.')
for x,title,body in [(56,'CONCEPT','Id  /  Title  /  Description\nCategory  /  UTC timestamps'),(527,'CONNECTION','Source  /  Target  /  Type\nNote  /  Unique ordered pair')]:
    s.rect(x,154,377,139,CARD,LINE,True)
    s.text(x+22,177,333,title,12,TEAL,True)
    s.text(x+22,216,333,body,17,leading=28)
s.line(442,222,516,222,TEAL,2,True)
for x,num,title,body in [(56,'01','Validate','Endpoints, lengths, types,\nnormalized titles.'),(345,'02','Delete atomically','Remove incident edges,\nthen remove the concept.'),(634,'03','Restore safely','Validate the whole backup;\ncommit into an empty atlas.')]:
    s.text(x,329,260,num,11,TEAL,True)
    s.text(x,355,270,title,21,bold=True)
    s.text(x,395,270,body,15,MUTED,leading=23)

s=new('Shortest-path discovery', 'BFS & COMPLEXITY', minutes='90 sec', notes='''This example uses the demonstration dataset. Spaced Repetition connects to Active Recall, which connects to Memory Palace. SQLite also connects to Memory Palace. The discovered chain from Spaced Repetition to SQLite is therefore three steps.
Discovery treats relationships as traversable in either direction. That is why it can move from Memory Palace to SQLite even though the stored semantic direction is the reverse. The stored direction and relationship type are not changed.
BFS starts with the source in a queue and explores neighbors layer by layer. A predecessor table records how each vertex was reached and marks it visited. When the destination is reached, following predecessors reconstructs the path. Cycles cannot enqueue the same vertex indefinitely.
For V vertices and E edges, both time and auxiliary space are O(V + E). All edges have equal traversal cost, so BFS finds a shortest chain. Weighted relations would need an algorithm such as Dijkstra's. A missing or disconnected endpoint returns no path; identical endpoints return a zero-step path.''')
s.heading('08 / BFS & COMPLEXITY','A shortest chain, one layer at a time')
xs=[119,355,591,827]
for i in range(3):s.line(xs[i]+18,222,xs[i+1]-18,222,GOLD,3,True)
for i,(x,label) in enumerate(zip(xs,['Spaced\nRepetition','Active\nRecall','Memory\nPalace','SQLite'])):
    s.circle(x-22,200,44,CARD,GOLD)
    s.text(x-14,208,28,str(i),18,GOLD,True,'ctr')
    s.text(x-83,266,166,label,18,bold=True,align='ctr')
s.text(56,336,848,'Queue → neighbors → visited vertices → predecessors → path',16,TEAL,True)
s.rect(56,382,249,75,CARD,LINE,True)
s.text(76,395,210,'O(V + E)',29,TEAL,True)
s.text(327,392,576,'Time and space for an unweighted graph.',19)
s.text(327,425,576,'Discovery can traverse a stored relationship backwards.',14,MUTED)

s=new('Live demonstration', 'FOUR-MINUTE WALKTHROUGH', True, minutes='4 min', notes='''Use a separate demonstration workspace. Restore docs/demo-atlas.json into an empty atlas and show the eight concepts and nine relationships. Avoid deleting personal data just to reset the demonstration.
First, select Breadth-First Search and inspect its connections. Explain that relationship notes describe why two concepts are linked. Second, create Learning Journal in the Learning category, then edit its description. Connect it to Active Recall with the Supports type and an explanatory note.
Third, find the path from Spaced Repetition to SQLite. Read the chain and point out that discovery can traverse a relationship backwards. Pan the map, drag a node, zoom, and reset. Switch to the library, use a search or category, and clear the filter.
Finally, export a backup. Open the deletion confirmation for Learning Journal, cancel once, and then confirm. Show that the other concepts remain without a dangling connection. Reload to demonstrate persistence. If time is short, prioritize create, connect, discover, and export. Keep the architecture slide available if the live server is unavailable.''')
s.heading('09 / LIVE DEMO','Capture. Connect. Discover. Preserve.')
steps=[('01','LOAD & INSPECT','Restore 8 concepts and 9 links.\nOpen a concept and read its relationships.'),('02','CREATE & CONNECT','Add Learning Journal, edit its description,\nand link it to Active Recall.'),('03','EXPLORE & DISCOVER','Find Spaced Repetition → SQLite.\nPan, drag, zoom, search, and switch views.'),('04','EXPORT & CLEAN UP','Download a backup, confirm deletion,\nand reload to check persistence.')]
for i,(num,title,body) in enumerate(steps):
    y=146+i*78
    s.circle(56,y+1,38,GREEN)
    s.text(61,y+10,28,num,13,'FFFFFF',True,'ctr')
    s.text(116,y+1,755,title,12,GREEN,True)
    s.text(116,y+24,755,body,16,INK,leading=21)

s=new('Verification', 'RECORDED QUALITY EVIDENCE', minutes='75 sec', notes='''The project has two executable assertion runners rather than a third-party test-framework runner. MemoryPalace.CoreChecks tests the independent graph algorithm and scoped-state behavior. MemoryPalace.Tests uses the actual ConceptService against a uniquely named temporary SQLite database, which it removes in a finally block.
On 15 November 2026, the complete solution built on macOS arm64 with .NET SDK 10.0.401 using the restored package assets. The build had zero errors and zero warnings. All 18 core checks and all 29 SQLite integration checks passed. The resolved assets included EF Core SQLite 10.0.12 and SQLitePCLRaw bundle 3.0.5.
The 47 assertions are not a measured line-coverage percentage. JavaScript syntax checks passed, and browser scenarios cover workflows and the new map interactions, but this environment denied Chromium launch. The browser and device matrix therefore remains pending. A fresh package restore and vulnerability audit are also separate from the successful cached-asset build. The QA document records these distinctions.''')
s.heading('10 / VERIFICATION','47 passing checks. Evidence by layer.')
for x,count,label,body in [(56,'18','CORE CHECKS','BFS, cycles, missing paths,\nUnicode search, and state.'),(494,'29','SQLITE CHECKS','Validation, CRUD, links,\nbackup integrity, and reads.')]:
    s.rect(x,153,410,189,CARD,LINE,True)
    s.text(x+25,172,130,count,61,TEAL,True)
    s.text(x+170,186,218,label,12,TEAL,True)
    s.text(x+170,222,218,body,15,MUTED,leading=24)
s.text(58,371,835,'BUILD   0 errors  /  0 warnings',23,bold=True)
s.text(58,414,835,'Browser and device verification: scenarios prepared; execution pending.',15,GOLD)
s.text(58,454,835,'macOS arm64  /  SDK 10.0.401  /  15 Nov 2026  /  Restored package assets',11,MUTED)

s=new('Trade-offs and next steps', 'ENGINEERING JUDGMENT', True, notes='''The current scope is a local personal workspace. It has no authentication, separate user-owned datasets, automatic cross-tab broadcasting, or optimistic concurrency token. Concurrent edits use a last-successful-write policy; lock or write errors produce recoverable feedback rather than automatic merging.
The whole personal atlas is loaded into memory. The graph is bounded to 60 visible nodes for readability and DOM size, with discovered path nodes prioritized. The library and complete text path remain available, but server-side pagination, full-text search, and load benchmarking are future work.
The next steps follow those limits: add identity and ownership before internet deployment, add migrations and concurrency handling as the schema evolves, and add pagination and larger graph layouts as data grows. Short-lived contexts, a service interface, and an independent graph algorithm provide clear extension points. These boundaries are deliberate scope decisions, not features that have already been completed.''')
s.heading('11 / TRADE-OFFS & NEXT STEPS','Keep the scope honest. Make growth possible.')
s.text(56,145,390,'CURRENT SCOPE',11,GREEN,True)
s.text(514,145,390,'NEXT ITERATION',11,GREEN,True)
for i,(a,b) in enumerate([('A local personal workspace','Authentication + ownership'),('Explicit refresh between tabs','Synchronization + concurrency tokens'),('In-memory atlas; 60 map nodes','Pagination + larger graph layouts'),('Initial database creation','Migration-based schema evolution')]):
    y=186+i*65
    s.line(56,y+42,904,y+42,'D3DDD7',1)
    s.text(56,y,400,a,18)
    s.line(470,y+11,493,y+11,GREEN,1.5,True)
    s.text(514,y,390,b,18)

s=new('Discussion', 'CONCLUSION & QUESTIONS', minutes='30 sec', notes='''To conclude, Memory Palace combines three capabilities: capture concise concepts, explain typed relationships, and discover a shortest chain between ideas. The project connects reusable Blazor components with scoped state, service-level validation, transactional SQLite storage, and a separately testable graph algorithm.
The running demonstration and recorded checks support the implemented scope. Browser verification and the larger deployment concerns remain clearly identified in the QA report and roadmap.
Thank you. We are ready to discuss the architecture, BFS, data-integrity rules, testing strategy, and the trade-offs behind the implementation. Keep the source, architecture document, and demonstration workspace available for questions. Both team members should be able to explain every layer, including the parts they did not present.''')
s.text(56,52,848,'12 / DISCUSSION',11,TEAL,True)
s.text(56,133,790,'Ideas are useful.\nConnections make them navigable.',40,bold=True,leading=51)
s.line(58,278,902,278,LINE,1)
for x,n,t in [(58,'01','Capture'),(346,'02','Connect'),(634,'03','Discover')]:
    s.text(x,316,250,n,11,TEAL,True)
    s.text(x,347,250,t,27,bold=True)
s.text(58,418,845,'Amirzhanuly Abay  /  Shikhiyev Alikhan',16,MUTED)
s.text(58,453,845,'Architecture  ·  Algorithms  ·  Integrity  ·  Testing',14,TEAL)

# Shared page furniture.
for number,s in enumerate(slides,1):
    s.line(56,494,904,494,'D2DBD5' if s.light else LINE,0.8)
    s.text(56,509,680,'MEMORY PALACE  /  KNOWLEDGE ATLAS',8,s.muted,True)
    s.text(825,506,79,f'{number:02d} / {len(slides):02d}',10,s.muted,align='r')
    for item in s.shapes:
        if item['kind']=='line':continue
        assert item['x']>=0 and item['y']>=0 and item['x']+item['w']<=W+1, (s.title,item)
        assert item['y']+item['h']<=H+1, (s.title,item)

# PowerPoint: editable DrawingML text, shapes, and connectors.
NS='xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"'
DECL='<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
PKG='http://schemas.openxmlformats.org/package/2006/relationships'
REL='http://schemas.openxmlformats.org/officeDocument/2006/relationships/'
def emu(n):return round(n*12700)
def solid(c):return f'<a:solidFill><a:srgbClr val="{c}"/></a:solidFill>'
def group():return '<p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>'
def xfrm(x,y,w,h):return f'<a:xfrm><a:off x="{emu(x)}" y="{emu(y)}"/><a:ext cx="{emu(w)}" cy="{emu(h)}"/></a:xfrm>'
def line_xml(color,width=1,arrow=False):return f'<a:ln w="{emu(width)}">{solid(color)}<a:prstDash val="solid"/>'+('<a:tailEnd type="triangle" w="sm" len="sm"/>' if arrow else '')+'</a:ln>'
def paragraph(line,item):
    sz=round(item['size']*100)
    return f'<a:p><a:pPr algn="{item["align"]}"><a:lnSpc><a:spcPts val="{round(item["leading"]*100)}"/></a:lnSpc><a:spcAft><a:spcPts val="0"/></a:spcAft></a:pPr><a:r><a:rPr lang="en-US" sz="{sz}" b="{int(item["bold"])}">{solid(item["color"])}<a:latin typeface="Arial"/></a:rPr><a:t xml:space="preserve">{escape(line)}</a:t></a:r><a:endParaRPr lang="en-US" sz="{sz}"/></a:p>'
def shape_xml(item,i):
    kind=item['kind'];name=escape(item.get('content',[''])[0] if kind=='text' else kind,{'"':'&quot;'})
    nv=f'<p:nvSpPr><p:cNvPr id="{i}" name="{name}"/><p:cNvSpPr'+(' txBox="1"' if kind=='text' else '')+'/><p:nvPr/></p:nvSpPr>'
    if kind=='line':
        x,y,x2,y2=item['x'],item['y'],item['x2'],item['y2']
        xf=xfrm(min(x,x2),min(y,y2),max(abs(x2-x),.01),max(abs(y2-y),.01)).replace('<a:xfrm>',f'<a:xfrm flipH="{int(x2<x)}" flipV="{int(y2<y)}">')
        return f'<p:cxnSp><p:nvCxnSpPr><p:cNvPr id="{i}" name="Connector {i}"/><p:cNvCxnSpPr/><p:nvPr/></p:nvCxnSpPr><p:spPr>{xf}<a:prstGeom prst="line"><a:avLst/></a:prstGeom>{line_xml(item["color"],item["width"],item["arrow"])}</p:spPr></p:cxnSp>'
    geom='ellipse' if kind=='circle' else ('roundRect' if item.get('radius') else 'rect')
    fill='<a:noFill/>' if kind=='text' else solid(item['fill'])
    stroke=line_xml(item['stroke']) if item.get('stroke') else '<a:ln><a:noFill/></a:ln>'
    sp=f'<p:sp>{nv}<p:spPr>{xfrm(item["x"],item["y"],item["w"],item["h"])}<a:prstGeom prst="{geom}"><a:avLst/></a:prstGeom>{fill}{stroke}</p:spPr>'
    if kind=='text':sp+='<p:txBody><a:bodyPr wrap="none" lIns="0" tIns="0" rIns="0" bIns="0" anchor="t"><a:noAutofit/></a:bodyPr><a:lstStyle/>'+''.join(paragraph(t,item) for t in item['content'])+'</p:txBody>'
    return sp+'</p:sp>'
def relationships(entries):return DECL+f'<Relationships xmlns="{PKG}">'+''.join(f'<Relationship Id="{i}" Type="{REL+t}" Target="{target}"/>' for i,t,target in entries)+'</Relationships>'

OUT.mkdir(exist_ok=True)
with zipfile.ZipFile(OUT/'Memory_Palace_Defense.pptx','w',zipfile.ZIP_DEFLATED) as z:
    def put(name,body):z.writestr(name,body if body.startswith('<?xml') else DECL+body)
    overrides=[('/ppt/presentation.xml','presentationml.presentation.main'),('/ppt/slideMasters/slideMaster1.xml','presentationml.slideMaster'),('/ppt/slideLayouts/slideLayout1.xml','presentationml.slideLayout'),('/ppt/notesMasters/notesMaster1.xml','presentationml.notesMaster'),('/ppt/theme/theme1.xml','theme')]
    overrides += [(f'/ppt/slides/slide{i}.xml','presentationml.slide') for i in range(1,len(slides)+1)]
    overrides += [(f'/ppt/notesSlides/notesSlide{i}.xml','presentationml.notesSlide') for i in range(1,len(slides)+1)]
    ct='<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/>'
    for name,t in overrides:ct+=f'<Override PartName="{name}" ContentType="application/vnd.openxmlformats-officedocument.{t}+xml"/>'
    ct+='<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/><Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/></Types>'
    put('[Content_Types].xml',ct)
    put('_rels/.rels',DECL+f'<Relationships xmlns="{PKG}"><Relationship Id="rId1" Type="{REL}officeDocument" Target="ppt/presentation.xml"/><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/><Relationship Id="rId3" Type="{REL}extended-properties" Target="docProps/app.xml"/></Relationships>')
    put('docProps/core.xml',f'<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:title>Memory Palace — Knowledge Atlas</dc:title><dc:subject>C# / .NET Cross-Platform Development</dc:subject><dc:creator>{escape(TEAM)}</dc:creator><dc:description>Twelve-slide final project defense with speaker notes.</dc:description><dc:language>en-US</dc:language></cp:coreProperties>')
    put('docProps/app.xml',f'<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"><Application>Memory Palace presentation builder</Application><PresentationFormat>On-screen Show (16:9)</PresentationFormat><Slides>{len(slides)}</Slides><Notes>{len(slides)}</Notes></Properties>')
    put('ppt/presentation.xml',f'<p:presentation {NS}><p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="rIdMaster"/></p:sldMasterIdLst><p:notesMasterIdLst><p:notesMasterId r:id="rIdNotes"/></p:notesMasterIdLst><p:sldIdLst>'+''.join(f'<p:sldId id="{255+i}" r:id="rIdSlide{i}"/>' for i in range(1,len(slides)+1))+f'</p:sldIdLst><p:sldSz cx="{emu(W)}" cy="{emu(H)}" type="screen16x9"/><p:notesSz cx="6858000" cy="9144000"/><p:defaultTextStyle/></p:presentation>')
    put('ppt/_rels/presentation.xml.rels',relationships([('rIdMaster','slideMaster','slideMasters/slideMaster1.xml'),('rIdNotes','notesMaster','notesMasters/notesMaster1.xml')]+[(f'rIdSlide{i}','slide',f'slides/slide{i}.xml') for i in range(1,len(slides)+1)]))
    clr='<p:clrMap accent1="accent1" accent2="accent2" accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6" bg1="lt1" bg2="lt2" folHlink="folHlink" hlink="hlink" tx1="dk1" tx2="dk2"/>'
    put('ppt/slideMasters/slideMaster1.xml',f'<p:sldMaster {NS}><p:cSld name="Memory Palace"><p:spTree>{group()}</p:spTree></p:cSld>{clr}<p:sldLayoutIdLst><p:sldLayoutId id="2147483649" r:id="rIdLayout"/></p:sldLayoutIdLst><p:txStyles><p:titleStyle/><p:bodyStyle/><p:otherStyle/></p:txStyles></p:sldMaster>')
    put('ppt/slideMasters/_rels/slideMaster1.xml.rels',relationships([('rIdLayout','slideLayout','../slideLayouts/slideLayout1.xml'),('rIdTheme','theme','../theme/theme1.xml')]))
    put('ppt/slideLayouts/slideLayout1.xml',f'<p:sldLayout {NS} type="blank" preserve="1"><p:cSld name="Blank"><p:spTree>{group()}</p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sldLayout>')
    put('ppt/slideLayouts/_rels/slideLayout1.xml.rels',relationships([('rIdMaster','slideMaster','../slideMasters/slideMaster1.xml')]))
    colors={'dk1':DARK,'lt1':WHITE,'dk2':INK,'lt2':PAPER,'accent1':TEAL,'accent2':GOLD,'accent3':'92ABFF','accent4':'C79BFF','accent5':'FF8FA3','accent6':'7FD4FF','hlink':TEAL,'folHlink':'92ABFF'}
    theme=f'<a:theme xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" name="Knowledge Atlas"><a:themeElements><a:clrScheme name="Atlas">'+''.join(f'<a:{k}><a:srgbClr val="{v}"/></a:{k}>' for k,v in colors.items())+'</a:clrScheme><a:fontScheme name="Arial"><a:majorFont><a:latin typeface="Arial"/><a:ea typeface=""/><a:cs typeface=""/></a:majorFont><a:minorFont><a:latin typeface="Arial"/><a:ea typeface=""/><a:cs typeface=""/></a:minorFont></a:fontScheme><a:fmtScheme name="Atlas"><a:fillStyleLst>'+solid(WHITE)*3+'</a:fillStyleLst><a:lnStyleLst>'+line_xml(LINE)*3+'</a:lnStyleLst><a:effectStyleLst>'+('<a:effectStyle><a:effectLst/></a:effectStyle>'*3)+'</a:effectStyleLst><a:bgFillStyleLst>'+solid(DARK)*3+'</a:bgFillStyleLst></a:fmtScheme></a:themeElements></a:theme>'
    put('ppt/theme/theme1.xml',theme)
    put('ppt/notesMasters/notesMaster1.xml',f'<p:notesMaster {NS}><p:cSld><p:spTree>{group()}</p:spTree></p:cSld>{clr}<p:notesStyle/></p:notesMaster>')
    put('ppt/notesMasters/_rels/notesMaster1.xml.rels',relationships([('rIdTheme','theme','../theme/theme1.xml')]))
    for i,s in enumerate(slides,1):
        put(f'ppt/slides/slide{i}.xml',f'<p:sld {NS}><p:cSld name="{escape(s.title)}"><p:bg><p:bgPr>{solid(s.bg)}<a:effectLst/></p:bgPr></p:bg><p:spTree>{group()}'+''.join(shape_xml(item,j+2) for j,item in enumerate(s.shapes))+'</p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sld>')
        put(f'ppt/slides/_rels/slide{i}.xml.rels',relationships([('rIdLayout','slideLayout','../slideLayouts/slideLayout1.xml'),('rIdNotes','notesSlide',f'../notesSlides/notesSlide{i}.xml')]))
        notes_item=dict(size=12,bold=False,color=INK,align='l',leading=16)
        paragraphs=''.join(paragraph(t,notes_item) for t in (s.title+' — '+s.minutes+'\n'+s.notes).split('\n'))
        note=f'<p:sp><p:nvSpPr><p:cNvPr id="2" name="Speaker Notes"/><p:cNvSpPr txBox="1"/><p:nvPr><p:ph type="body" idx="1"/></p:nvPr></p:nvSpPr><p:spPr/><p:txBody><a:bodyPr/><a:lstStyle/>{paragraphs}</p:txBody></p:sp>'
        put(f'ppt/notesSlides/notesSlide{i}.xml',f'<p:notes {NS}><p:cSld><p:spTree>{group()}{note}</p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:notes>')
        put(f'ppt/notesSlides/_rels/notesSlide{i}.xml.rels',relationships([('rIdSlide','slide',f'../slides/slide{i}.xml'),('rIdMaster','notesMaster','../notesMasters/notesMaster1.xml')]))

# Matching PDF: the same scene graph, not screenshots of slides.
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
font_dir=Path('/System/Library/Fonts/Supplemental')
if (font_dir/'Arial.ttf').exists():
    pdfmetrics.registerFont(TTFont('Atlas',(font_dir/'Arial.ttf').as_posix()))
    pdfmetrics.registerFont(TTFont('AtlasBold',(font_dir/'Arial Bold.ttf').as_posix()))
    normal,bold='Atlas','AtlasBold'
else:normal,bold='Helvetica','Helvetica-Bold'
pdf=canvas.Canvas(str(OUT/'Memory_Palace_Defense.pdf'),pagesize=(W,H))
pdf.setTitle('Memory Palace — Knowledge Atlas')
pdf.setAuthor(TEAM)
text_overflows=[]
for s in slides:
    pdf.setFillColor(HexColor('#'+s.bg));pdf.rect(0,0,W,H,fill=1,stroke=0)
    for item in s.shapes:
        k=item['kind'];x=item['x'];y=item['y']
        if k=='text':
            f=bold if item['bold'] else normal
            pdf.setFont(f,item['size']);pdf.setFillColor(HexColor('#'+item['color']))
            for j,line in enumerate(item['content']):
                width=pdfmetrics.stringWidth(line,f,item['size'])
                if width>item['w']+1:text_overflows.append((s.title,line,round(width),item['w']))
                xx=x+(item['w']-width)/2 if item['align']=='ctr' else (x+item['w']-width if item['align']=='r' else x)
                pdf.drawString(xx,H-y-item['size']-j*item['leading'],line)
        elif k=='line':
            x2,y2=item['x2'],item['y2']
            pdf.setStrokeColor(HexColor('#'+item['color']));pdf.setLineWidth(item['width'])
            pdf.line(x,H-y,x2,H-y2)
            if item['arrow']:
                theta=math.atan2(y2-y,x2-x);size=6
                path=pdf.beginPath();path.moveTo(x2,H-y2)
                for angle in (theta+2.65,theta-2.65):path.lineTo(x2+size*math.cos(angle),H-y2-size*math.sin(angle))
                path.close();pdf.setFillColor(HexColor('#'+item['color']));pdf.drawPath(path,fill=1,stroke=0)
        else:
            pdf.setFillColor(HexColor('#'+item['fill']))
            if item.get('stroke'):pdf.setStrokeColor(HexColor('#'+item['stroke']));pdf.setLineWidth(1)
            kwargs=dict(fill=1,stroke=int(bool(item.get('stroke'))))
            if k=='circle':pdf.ellipse(x,H-y-item['h'],x+item['w'],H-y,**kwargs)
            elif item.get('radius'):pdf.roundRect(x,H-y-item['h'],item['w'],item['h'],8,**kwargs)
            else:pdf.rect(x,H-y-item['h'],item['w'],item['h'],**kwargs)
    pdf.showPage()
pdf.save()
assert not text_overflows, f'Text exceeds its box: {text_overflows}'

# Keep the script and the PowerPoint speaker notes synchronized.
script_path=OUT/'PRESENTATION.md'
old=script_path.read_text() if script_path.exists() else ''
qa=old.split('## Defense Q&A',1)[-1] if '## Defense Q&A' in old else ''
intro='''# Memory Palace — Defense Script

**Course:** C# / .NET Cross-Platform Development

**Team:** Amirzhanuly Abay and Shikhiyev Alikhan

**Format:** 12 slides, approximately 18–20 minutes including a four-minute live demo.

Open `Memory_Palace_Defense.pptx` in PowerPoint, Keynote, or a compatible presentation editor. All slide text and diagrams are editable. Speaker notes are included for every slide. Use `Memory_Palace_Defense.pdf` for a read-only copy or direct upload.

Both names are already entered on the title and closing slides. To change them, edit those text boxes and this script. To rebuild the files from source, run `python3 tools/build_presentation.py` from the repository root after installing the dependencies in `tools/presentation-requirements.txt`. The PDF and PowerPoint are built from the same layouts; the PDF is not an Office-rendered export.

Both students should rehearse the entire implementation and be ready to explain every layer. Use a separate demo workspace and consult `QA.md` for current verification status.

'''
script_path.write_text(intro+'\n\n'.join(f'## Slide {i} — {s.title} · {s.minutes}\n\n'+s.notes for i,s in enumerate(slides,1))+'\n\n## Defense Q&A'+qa)
print(f'Created {len(slides)} editable slides, {len(slides)} speaker-note pages, and a matching PDF.')
