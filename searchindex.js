Search.setIndex({docnames:["glossary","index","license","reference/client","reference/index","reference/logging","reference/models","reference/oauth2","user/getcredentials","user/index","user/installation","user/quickstart","user/whatispyclarify"],envversion:{"sphinx.domains.c":2,"sphinx.domains.changeset":1,"sphinx.domains.citation":1,"sphinx.domains.cpp":4,"sphinx.domains.index":1,"sphinx.domains.javascript":2,"sphinx.domains.math":2,"sphinx.domains.python":3,"sphinx.domains.rst":2,"sphinx.domains.std":2,sphinx:56},filenames:["glossary.rst","index.rst","license.rst","reference/client.rst","reference/index.rst","reference/logging.rst","reference/models.rst","reference/oauth2.rst","user/getcredentials.rst","user/index.rst","user/installation.rst","user/quickstart.rst","user/whatispyclarify.rst"],objects:{"":[[4,0,0,"-","pyclarify"]],"pyclarify.client":[[3,1,1,"","APIClient"],[3,1,1,"","RawClient"],[3,3,1,"","increment_id"]],"pyclarify.client.APIClient":[[3,2,1,"","insert"],[3,2,1,"","publish_signals"],[3,2,1,"","save_signals"],[3,2,1,"","select_items"],[3,2,1,"","select_signals"]],"pyclarify.client.RawClient":[[3,2,1,"","authenticate"],[3,2,1,"","create_payload"],[3,2,1,"","get_token"],[3,2,1,"","send"],[3,2,1,"","update_headers"]],"pyclarify.models":[[6,0,0,"-","auth"],[6,0,0,"-","data"],[6,0,0,"-","requests"],[6,0,0,"-","response"]],"pyclarify.models.auth":[[6,1,1,"","ClarifyCredential"],[6,1,1,"","Credential"],[6,1,1,"","OAuthRequestBody"],[6,1,1,"","OAuthResponse"]],"pyclarify.models.auth.ClarifyCredential":[[6,4,1,"","apiUrl"],[6,4,1,"","credentials"],[6,4,1,"","integration"]],"pyclarify.models.auth.Credential":[[6,4,1,"","clientId"],[6,4,1,"","clientSecret"],[6,4,1,"","type"]],"pyclarify.models.auth.OAuthRequestBody":[[6,4,1,"","audience"],[6,4,1,"","client_id"],[6,4,1,"","client_secret"],[6,4,1,"","grant_type"]],"pyclarify.models.auth.OAuthResponse":[[6,4,1,"","access_token"],[6,4,1,"","expires_in"],[6,4,1,"","scope"],[6,4,1,"","token_type"]],"pyclarify.models.data":[[6,4,1,"","AnnotationKey"],[6,1,1,"","DataFrame"],[6,1,1,"","DataQuery"],[6,1,1,"","GenericSummary"],[6,4,1,"","InputID"],[6,1,1,"","InsertSummary"],[6,1,1,"","Item"],[6,4,1,"","LabelsKey"],[6,4,1,"","ResourceID"],[6,1,1,"","ResourceMetadata"],[6,1,1,"","ResourceQuery"],[6,4,1,"","SHA1Hash"],[6,1,1,"","SaveSummary"],[6,1,1,"","Signal"],[6,1,1,"","SignalInfo"],[6,1,1,"","SourceTypeSignal"],[6,1,1,"","TypeSignal"],[6,3,1,"","merge"]],"pyclarify.models.data.DataFrame":[[6,4,1,"","series"],[6,4,1,"","times"]],"pyclarify.models.data.DataQuery":[[6,4,1,"","before"],[6,4,1,"","include"],[6,4,1,"","notBefore"],[6,4,1,"","rollup"]],"pyclarify.models.data.GenericSummary":[[6,4,1,"","created"],[6,4,1,"","id"]],"pyclarify.models.data.InsertSummary":[[6,4,1,"","created"],[6,4,1,"","id"]],"pyclarify.models.data.Item":[[6,4,1,"","visible"]],"pyclarify.models.data.ResourceMetadata":[[6,4,1,"","contentHash"],[6,4,1,"","createdAt"],[6,4,1,"","updatedAt"]],"pyclarify.models.data.ResourceQuery":[[6,4,1,"","filter"],[6,4,1,"","include"],[6,4,1,"","limit"],[6,4,1,"","skip"]],"pyclarify.models.data.SaveSummary":[[6,4,1,"","updated"]],"pyclarify.models.data.Signal":[[6,4,1,"","inputId"],[6,4,1,"","item"],[6,4,1,"","meta"]],"pyclarify.models.data.SignalInfo":[[6,1,1,"","Config"],[6,4,1,"","annotations"],[6,4,1,"","description"],[6,4,1,"","engUnit"],[6,4,1,"","enumValues"],[6,4,1,"","gapDetection"],[6,4,1,"","labels"],[6,4,1,"","name"],[6,4,1,"","sampleInterval"],[6,4,1,"","sourceType"],[6,4,1,"","type"]],"pyclarify.models.data.SignalInfo.Config":[[6,4,1,"","extra"],[6,4,1,"","json_encoders"]],"pyclarify.models.data.SourceTypeSignal":[[6,4,1,"","aggregation"],[6,4,1,"","measurement"],[6,4,1,"","prediction"]],"pyclarify.models.data.TypeSignal":[[6,4,1,"","enum"],[6,4,1,"","numeric"]],"pyclarify.models.requests":[[6,1,1,"","AdminParams"],[6,1,1,"","ApiMethod"],[6,1,1,"","ClarifyParams"],[6,1,1,"","InclusionParams"],[6,1,1,"","InsertParams"],[6,4,1,"","IntegrationID"],[6,1,1,"","IntegrationParams"],[6,1,1,"","JSONRPCRequest"],[6,4,1,"","LimitSelectItems"],[6,4,1,"","LimitSelectSignals"],[6,1,1,"","PublishSignalsParams"],[6,1,1,"","QueryParams"],[6,1,1,"","RequestParams"],[6,4,1,"","ResourceID"],[6,1,1,"","SaveSignalsParams"],[6,1,1,"","SelectItemsDataParams"],[6,1,1,"","SelectItemsItemsParams"],[6,1,1,"","SelectItemsParams"],[6,1,1,"","SelectSignalsItemsParams"],[6,1,1,"","SelectSignalsParams"],[6,1,1,"","SelectSignalsSignalsParams"]],"pyclarify.models.requests.AdminParams":[[6,4,1,"","integration"]],"pyclarify.models.requests.ApiMethod":[[6,4,1,"","insert"],[6,4,1,"","publish_signals"],[6,4,1,"","save_signals"],[6,4,1,"","select_items"],[6,4,1,"","select_signals"]],"pyclarify.models.requests.InclusionParams":[[6,4,1,"","include"]],"pyclarify.models.requests.InsertParams":[[6,4,1,"","data"]],"pyclarify.models.requests.IntegrationParams":[[6,4,1,"","integration"]],"pyclarify.models.requests.JSONRPCRequest":[[6,1,1,"","Config"],[6,4,1,"","id"],[6,4,1,"","jsonrpc"],[6,4,1,"","method"],[6,4,1,"","params"]],"pyclarify.models.requests.JSONRPCRequest.Config":[[6,4,1,"","json_encoders"]],"pyclarify.models.requests.PublishSignalsParams":[[6,4,1,"","createOnly"],[6,4,1,"","itemsBySignal"]],"pyclarify.models.requests.QueryParams":[[6,4,1,"","filter"],[6,4,1,"","include"],[6,4,1,"","skip"]],"pyclarify.models.requests.SaveSignalsParams":[[6,4,1,"","createOnly"],[6,4,1,"","inputs"]],"pyclarify.models.requests.SelectItemsDataParams":[[6,4,1,"","before"],[6,4,1,"","notBefore"],[6,4,1,"","rollup"]],"pyclarify.models.requests.SelectItemsItemsParams":[[6,4,1,"","limit"]],"pyclarify.models.requests.SelectItemsParams":[[6,4,1,"","data"],[6,4,1,"","items"]],"pyclarify.models.requests.SelectSignalsItemsParams":[[6,4,1,"","include"]],"pyclarify.models.requests.SelectSignalsParams":[[6,4,1,"","items"],[6,4,1,"","signals"]],"pyclarify.models.requests.SelectSignalsSignalsParams":[[6,4,1,"","limit"]],"pyclarify.models.response":[[6,1,1,"","Error"],[6,1,1,"","ErrorData"],[6,1,1,"","GenericResponse"],[6,1,1,"","InsertResponse"],[6,1,1,"","PublishSignalsResponse"],[6,1,1,"","Response"],[6,1,1,"","SaveSignalsResponse"],[6,1,1,"","SelectItemsResponse"],[6,1,1,"","SelectSignalsResponse"]],"pyclarify.models.response.Error":[[6,4,1,"","code"],[6,4,1,"","data"],[6,4,1,"","message"]],"pyclarify.models.response.ErrorData":[[6,4,1,"","params"],[6,4,1,"","trace"]],"pyclarify.models.response.GenericResponse":[[6,4,1,"","error"],[6,4,1,"","id"],[6,4,1,"","jsonrpc"],[6,4,1,"","result"]],"pyclarify.models.response.InsertResponse":[[6,4,1,"","signalsByInput"]],"pyclarify.models.response.PublishSignalsResponse":[[6,4,1,"","itemsBySignal"]],"pyclarify.models.response.Response":[[6,4,1,"","result"]],"pyclarify.models.response.SaveSignalsResponse":[[6,4,1,"","signalsByInput"]],"pyclarify.models.response.SelectItemsResponse":[[6,4,1,"","data"],[6,4,1,"","items"]],"pyclarify.models.response.SelectSignalsResponse":[[6,4,1,"","items"],[6,4,1,"","signals"]],"pyclarify.oauth2":[[7,5,1,"","AuthError"],[7,1,1,"","GetToken"]],"pyclarify.oauth2.GetToken":[[7,2,1,"","get_new_token"],[7,2,1,"","get_token"],[7,2,1,"","read_credentials"]],pyclarify:[[3,0,0,"-","client"],[7,0,0,"-","oauth2"]]},objnames:{"0":["py","module","Python module"],"1":["py","class","Python class"],"2":["py","method","Python method"],"3":["py","function","Python function"],"4":["py","attribute","Python attribute"],"5":["py","exception","Python exception"]},objtypes:{"0":"py:module","1":"py:class","2":"py:method","3":"py:function","4":"py:attribute","5":"py:exception"},terms:{"0":[2,3,6,7],"00":3,"03":5,"04":5,"06z":[5,11],"09t21":11,"1":[2,3,5,6,11],"10":[3,6],"1000":3,"10t21":[3,11],"10t22":3,"11":11,"11t21":5,"12t21":11,"2":[2,3,5,6,7,11],"20":3,"2004":2,"2021":[1,3,5,6,7,11],"22":1,"3":[3,11],"32602":3,"3339":3,"4":11,"5":11,"50":[2,3,5,6,11],"9":2,"case":3,"class":[2,3,6,7,11],"default":3,"do":[2,3,4,11],"enum":6,"float":[3,6],"function":[3,4,6],"import":[2,3,5,11],"int":[3,6],"new":[3,5,7],"null":3,"return":[3,6,7],"true":[3,11],"while":2,A:[2,3,5],AND:2,AS:[2,3,6,7],By:3,FOR:2,For:[0,2,3,11],IS:[2,3,6,7],If:[2,3],In:[0,2,3,8],Not:2,OF:[2,3,6,7],OR:[2,3,6,7],The:[2,3,7],To:[0,2,3,10,11],abl:11,aboui:0,about:11,abov:2,accept:2,access:[3,5,7,11],access_token:6,act:2,ad:3,add:[0,2],addendum:2,addit:2,adjust:3,admin:[3,6],adminparam:6,advis:2,after:3,against:2,aggreg:6,agre:[2,3,6,7],agreement:2,alia:6,all:[2,3,6],alleg:2,alon:2,along:2,alongsid:2,alreadi:3,also:2,alwai:11,an:[0,2,3,4,6,7,11],ani:[2,3,6,7],annot:[2,6],annotationkei:6,apach:[2,3,6,7],api:[3,6],apicli:[3,5,11],apimethod:6,apiurl:6,app:[3,7],appear:[2,7],appendix:2,appli:2,applic:[2,3,6,7],appropri:2,ar:[0,2,3,4],archiv:2,argument:[3,11],aris:2,around:3,arrai:3,asctim:5,assert:2,associ:2,assum:2,attach:2,attribut:2,audienc:6,auth:4,authent:[3,7],autherror:7,author:2,authorship:2,avail:2,base:[2,3,6,7],base_url:3,basemodel:6,basi:[2,3,6,7],basicconfig:5,bearer:6,bedroom:[3,11],been:2,befor:[3,6,11],behalf:2,being:3,below:2,benefici:2,bind:2,bit:11,boilerpl:2,bool:[3,6],bracket:2,bucket:3,call:[3,5,11],can:[0,5,8,12],cannot:2,carri:2,caus:2,celsiu:0,chang:2,charact:2,charg:2,check:7,choos:2,claim:2,clarifi:[0,3,5,6,7,8,12],clarify_credenti:[3,7],clarifycredenti:6,clarifyparam:6,click:[3,8,11],client:[4,5,11],client_credenti:6,client_id:6,client_secret:6,clientid:6,clientsecret:6,code:[2,3,6],combin:[2,3],comment:2,commerci:2,common:2,commun:2,compil:2,compli:2,complianc:[2,3,6,7],comput:2,concaten:6,condit:[2,3,6,7],config:6,configur:[2,3],consequenti:2,consist:2,conspicu:2,constitut:2,constrainedintvalu:6,constrainedstrvalu:6,constru:2,contain:[2,3,5,6],content:[2,3,7],contenthash:6,contract:2,contribut:2,contributor:2,contributori:2,control:2,convers:2,copi:[2,3,6,7],copyright:[2,3,6,7],counterclaim:2,creat:[0,3,5,6,8,11,12],create_payload:3,created_onli:3,createdat:6,createonli:[3,6,11],credenti:[3,5,6,7,9,11],cross:2,current:[0,3],customari:2,damag:2,data:[0,3,4,5,12],datafram:[3,5,6,11],dataqueri:6,date:2,datetim:[3,6],dd:3,decor:3,defend:2,defin:2,definit:2,deliber:2,deriv:2,describ:[2,3,4],descript:[2,3,6,11],design:2,detail:4,determin:2,develop:11,dict:[3,6,7],dictionari:[3,7,11],differ:2,direct:2,disclaim:2,discuss:2,displai:2,distribut:[2,3,6,7],document:[1,2,11],doe:2,don:2,done:6,download:[3,7,8],durat:3,each:[2,3],easi:11,easier:2,easili:12,editori:2,either:[2,3,6,7],elabor:2,electron:2,els:7,empti:3,enabl:11,enclos:2,end:[2,3],engunit:6,entiti:2,entri:6,enumer:6,enumvalu:6,equal:3,error:[3,6,7],error_descript:7,errordata:[3,6],even:2,evenli:3,event:2,exampl:[0,2,3,4],except:[2,3,6,7],exclud:2,exclus:[2,3],execut:2,exercis:2,exist:[3,7],expir:7,expires_in:6,explicitli:2,expos:[3,11],express:[2,3,6,7],extra:6,fahrenheit:0,failur:2,fals:[3,6,11],fast:11,fee:2,ffffff:3,field:[2,3],fifti:2,file:[2,3,5,6,7],filenam:5,filter:[3,6,11],find:[8,11],first:[3,10,11],fit:2,follow:[2,3],forbid:6,form:[2,3],format:[2,3,5,11],frame:6,free:2,from:[0,2,3,7,11],full:3,func:3,gapdetect:6,gener:[2,7],genericrespons:6,genericsummari:6,get:[3,7],get_new_token:7,get_token:[3,7],gettoken:[3,7],give:2,given:[3,6],glossari:1,go:[0,8],goodwil:2,govern:[2,3,6,7],grant:2,grant_typ:6,grossli:2,guid:1,ha:[0,2,3,7],harmless:2,have:[0,2,8,11],header:3,here:[3,11],herebi:2,herein:2,hh:3,hold:2,home:[3,11],how:[2,8,11],howev:2,http:[2,3,6,7],humid:11,i:2,id1:[3,11],id2:11,id:[3,5,6,11],identif:2,identifi:[2,3],ii:2,iii:2,impli:[2,3,6,7],improv:2,inabl:2,incident:2,includ:[2,3,4,6,11],inclus:[2,3],inclusionparam:6,incorpor:2,increment:3,increment_id:3,incur:2,indemn:2,indemnifi:2,index:1,indic:[1,2],indirect:2,individu:2,info:5,inform:[0,1,2,3,11],infring:2,input:[3,6,11],input_id:3,inputid:[3,6],insert:[3,5,6,11],insertparam:6,insertrespons:[3,6],insertsummari:[3,6],instal:9,instanc:3,institut:2,integr:[3,6,8,11],integrationid:6,integrationparam:6,intention:2,interact:12,interfac:2,invalid:3,io:6,irrevoc:2,issu:2,item:[0,3,6,12],item_id:[3,11],item_id_avg:3,item_id_count:3,item_id_max:3,item_id_min:3,item_id_sum:3,item_nam:[3,11],itemsbysign:[3,6,11],its:[2,3],januari:2,json:[3,5,7,11],json_encod:6,jsonrpc:[3,6],jsonrpcrequest:6,kei:3,kind:[2,3,6,7],know:11,label:[3,6,11],labelskei:6,languag:[2,3,6,7],last:1,law:[2,3,6,7],lawsuit:2,least:2,legal:2,length:3,let:12,level:5,levelnam:5,liabil:2,liabl:2,licens:[1,3,6,7],licensor:2,limit:[2,3,6,7],limitselectitem:6,limitselectsign:6,link:2,list:[2,3,6],liter:6,litig:2,live:11,ll:11,locat:[3,11],log:[4,8],loss:2,made:2,mai:[2,3,6,7],mail:2,main:6,make:2,malfunct:2,manag:2,manual:4,map:[3,6],mark:2,match:3,max:3,mean:2,measur:6,mechan:2,media:2,medium:2,meet:2,merchant:2,mere:2,merg:6,messag:[3,5,6],meta:[1,3,6],metadata:[0,3,12],method:[3,6,11],min:3,mirror:3,mm:3,model:[3,4,11],modif:2,modifi:2,modul:[1,4],more:[0,2,3,6,11],most:3,multipl:3,must:[2,3,11],n:3,name:[2,3,6,11],necessarili:2,need:11,neglig:2,newli:11,non:2,none:[3,6,11],normal:2,notbefor:[3,6],noth:2,notic:2,notwithstand:2,nov:1,now:[5,11],number:3,numer:[3,6],oauth2:[3,7],oauthrequestbodi:6,oauthrespons:6,object:[2,3,4,6,7],oblig:2,obtain:[2,3,6,7],offer:2,old:7,omit:3,onc:[8,11],one:[0,2,3,7,11],onli:[2,3],option:[3,6],org:[2,3,6,7],origin:2,other:2,otherwis:[2,3],out:2,outstand:2,overlap:6,own:2,owner:2,ownership:2,packag:0,page:[1,2],param:[3,6,11],paramet:[3,6,7],part:2,parti:2,particular:2,pass:3,patent:2,path:[3,7,11],payload:3,percent:2,perform:2,permiss:[2,3,6,7],perpetu:2,pertain:2,pi:[3,11],pip:10,place:2,point:3,pop:8,possibl:[2,3],post:3,power:2,predict:6,prefer:2,prepar:2,print:[2,11],product:2,promin:2,provid:[2,11],publicli:2,publish:3,publish_sign:[3,6,11],publishsign:[3,6,11],publishsignalsparam:6,publishsignalsrespons:6,purpos:2,put:0,py:3,pyclarifi:[0,10],pydant:[3,6],python:[3,11],queri:3,queryparam:6,quickstart:9,raspberri:[3,11],rawclient:3,read:[7,11,12],read_credenti:7,readabl:2,reason:2,receiv:2,recipi:2,recommend:[2,3,11],redistribut:2,refer:1,refresh:11,regard:2,remain:2,render:3,replac:2,repres:2,reproduc:2,reproduct:2,request:[3,4],requestparam:6,requir:[2,3,6,7],resourc:3,resourceid:6,resourcemetadata:6,resourcequeri:6,respons:[2,3,4,11],result:[2,3,6],retain:2,retriev:11,revis:2,rfc3339:3,rfc:3,right:2,risk:2,roll:3,rollup:[3,6],room:11,royalti:2,rpc:3,run:5,s:[1,2,5,11],same:[2,3],sampleinterv:6,save:3,save_sign:[3,6,11],savesign:[3,6],savesignalsparam:6,savesignalsrespons:[3,6],savesummari:[3,6],scope:6,search:1,section:2,see:[2,3,6,7,11],select:3,select_item:[3,6,11],select_sign:[3,6,11],selectitem:[3,6],selectitemsdataparam:6,selectitemsitemsparam:6,selectitemsparam:6,selectitemsrespons:6,selectsign:[3,6],selectsignalsitemsparam:6,selectsignalsparam:6,selectsignalsrespons:6,selectsignalssignalsparam:6,sell:2,send:3,sent:2,separ:2,seri:[3,5,6,11],servic:2,set:3,sha1hash:6,shall:2,share:2,should:[2,11],signal:[0,3,6,8,12],signal_1:11,signal_2:11,signal_id1:3,signal_id2:3,signal_id:[3,11],signalinfo:[3,6,11],signalsbyinput:[3,6],singl:6,size:3,skip:[3,6],softwar:[2,3,6,7],sole:2,sourc:[2,3,11],sourcetyp:6,sourcetypesign:6,special:2,specif:[2,3,6,7],specifi:[3,5],ss:3,start:[3,11],state:2,statement:2,step:[3,11],stoppag:2,store:0,str:[3,6,7],string:[3,11],subject:2,sublicens:2,submiss:2,submit:2,subsequ:2,supersed:2,support:2,syntax:2,system:2,t:[2,3],tabl:1,take:11,temperatur:[0,3,11],term:2,termin:2,text:2,than:0,thei:4,them:[8,11],theori:2,thereof:2,thi:[2,3,4,6,7,11],third:2,those:2,through:2,time:[3,5,6,11],timedelta:6,timedelta_isoformat:6,timeseri:3,timestamp:[3,6],titl:2,token:[3,7],token_typ:6,tool:12,tort:2,trace:[3,6],trace_id:3,track:2,trade:2,trademark:2,transfer:2,transform:2,translat:2,tune:3,tutori:11,two:0,type:[2,3,6,7],typesign:6,under:[2,3,6,7,8],union:[2,3,6],uniqu:3,unit:0,unless:[2,3,6,7],up:[3,8],updat:[0,1,3,6,11,12],update_head:3,updatedat:6,us:[2,3,6,7,10,11],user:[1,7],usign:0,v1:6,valid:[3,6],valu:[3,6],variabl:3,verbal:2,version:[0,2,3,6,7],visibl:6,wa:[2,3],wai:11,want:8,warranti:[2,3,6,7],we:2,websit:0,welcom:1,what:[4,9],when:[5,7,11],where:[0,2,3],wheresavesummari:3,wherev:2,whether:2,which:[0,2,3,8,11],whole:2,whom:2,window:[3,6,8],within:2,without:[2,3,6,7],work:2,worldwid:2,wrap:3,write:[2,3,6,7],written:2,www:[2,3,6,7],ye:7,you:[0,2,3,6,7,8,11,12],your:[2,8,11],yyyi:[2,3],z:3},titles:["Glossary","PyClarify v0.1.0 Manual","PyClarify license","PyClarify Client","PyClarify Reference","PyClarify logging","pyclarify.models","PyClarify Auth","Credentials","PyClarify user guide","Installation","PyClarify quickstart","What is PyClarify?"],titleterms:{"0":1,"1":1,add:11,an:5,auth:[6,7],clarifi:11,client:3,credenti:8,data:[6,11],exampl:[5,11],get:11,glossari:0,guid:9,instal:10,interact:11,item:11,licens:2,log:5,manual:1,meta:11,metadata:11,model:6,modul:6,prerequisit:11,publish:11,pyclarifi:[1,2,3,4,5,6,7,9,11,12],quickstart:11,refer:4,request:6,respons:6,signal:11,user:9,v0:1,what:12,write:11}})