from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy
from flask import redirect
import json, codecs
from sqlalchemy.exc import IntegrityError
import matplotlib
import matplotlib.pyplot as plt

app  = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///userCredentials.sqlite3"
db = SQLAlchemy(app)

app.app_context().push()

#Models
#User Credential Table

class AdminCred(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(), unique=True)
    pasword = db.Column(db.String())

class SponsorCred(db.Model):
    __tablename__ = "sponsor_cred"
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(), unique=True)
    pasword = db.Column(db.String())
    industry_type = db.Column(db.String())
    budget = db.Column(db.Integer)
    #add dob or adress or mobile number
class InfluencerCred(db.Model):
    __tablename__ = "influencer_cred"
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(), unique=True)
    pasword = db.Column(db.String())
    rech = db.Column(db.Integer)
    bio = db.Column(db.String())

class Campaigns(db.Model):
    __tablename__ = "campaigns"
    id = db.Column(db.Integer, primary_key = True)
    campaign_name = db.Column(db.String(), unique = True)
    campaign_id = db.Column(db.Integer, unique = True)
    sponsor_id = db.Column(db.Integer, db.ForeignKey('sponsor_cred.id'))
    price = db.Column(db.Integer, nullable = False)
    progress = db.Column(db.Integer)
    duration = db.Column(db.String())
    industry_type = db.Column(db.String())
    description = db.Column(db.String())
    goals = db.Column(db.String())

class RequestsandStaus(db.Model):
    __tablename__ = "requestsandstatus"
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaigns.id'))
    influencer_id = db.Column(db.String(), db.ForeignKey('influencer_cred.id'))
    status = db.Column(db.String())
    message = db.Column(db.String())
    negoPrice = db.Column(db.Integer)
    __table_args__ = (
        db.PrimaryKeyConstraint(campaign_id, influencer_id),
    )
db.create_all()

#Dashboards
#Sponser
@app.route('/sponsorDashboard/<campaign_id>/<influencer_id>')
def sponsorDashboard(campaign_id = None, influencer_id  = None):
    if campaign_id != "None" and influencer_id != "None":
        campaign_id = int(campaign_id.strip())
        influencer_id = str(influencer_id.strip())
    f = open("sponsor.txt","r")
    username = f.read()
    username = json.loads(username)["username"]
    print(username)
    sponsor_id = None
    campaigns_data = {}
    campaign_status = {}
    global data
    data = {}
    global formData 
    formData = {}
    view=''
    sponsor_data = {} # to display on dashboard
    influencer_data = {} # to display when sponsor wants to see who sent request
    #fetch first sponsor id to use id in other tables
    sponsor_data = SponsorCred.query.filter_by(username = username).first()
    sponsor_id = sponsor_data.id
    #to use campaing id who belong to sponsor id in request table
    campaigns_data = Campaigns.query.filter_by(sponsor_id = sponsor_id).all()
    print("Campaigns ", campaigns_data)
    #select list of campaign id and store them in campaign data
    for i in campaigns_data:
        #all campaigns referning to sponsor_id
        all_campaigns = RequestsandStaus.query.filter_by(campaign_id = i.id).all()
        
        for j in all_campaigns:
            print(j)
            c = Campaigns.query.filter_by(id = j.campaign_id).first()
            d = InfluencerCred.query.filter_by(id = j.influencer_id).first()
            if (j.influencer_id == 0 or j.influencer_id == '0'):
                print('ifnluencer 0')
                
                data = {
                    "campaign_id" : j.campaign_id,
                    "campaign_n": c.campaign_name,
                    "goals" : c.goals,
                    "description" : c.description,
                    "price" : c.price,
                    "progress" : c.progress,
                    "duration" : c.duration,
                    "influencer_id" : j.influencer_id,
                    "influencer_name" : None,
                    "influencer_reac" : None,
                    "influencer_bio" : None,
                    'negoPrice' : j.negoPrice,
                    'message' : j.message,
                }
            else:
                print('influencer not 0')
                data = {
                    "campaign_id" : j.campaign_id,
                    "campaign_n": c.campaign_name,
                    "goals" : c.goals,
                    "description" : c.description,
                    "price" : c.price,
                    "progress" : c.progress,
                    "duration" : c.duration,
                    "influencer_id" : j.influencer_id,
                    "influencer_name" : d.username,
                    "influencer_reac" : d.rech,
                    "influencer_bio" : d.bio,
                    'negoPrice' : j.negoPrice,
                    'message' : j.message,
                }
            print(data)
            print(str(campaign_id),str(data["campaign_id"]))
            if str(campaign_id) == str(data["campaign_id"]):
                
                formData = data.copy()
                print("qweqewrreqeqweqeqewweqweqe : ", formData, data)
                if j.status == "Pr_A_In" or j.status == "Pr_A_C":
                    view = "Active Campaigns"
                elif j.status == "Pr_P_C" and j.negoPrice == data["price"]:
                    view = "New Requests"
                elif j.status == "Pr_P_C" and j.negoPrice != data["price"]:
                    view = "Nego Requests"
                elif j.status == "Pr_P_In":
                    view = "Pending Requests"
                elif j.status == "P_P_In":
                    view = "Public Requests"
                print('view ', view)
                formData["view"] = view
            print('wewwwwwwwwwwwrrrrrrrrrrr',formData, j.status)

            #print(data)
            campaignOriginalPrice = Campaigns.query.filter_by(campaign_id = j.campaign_id).first()
            campaignOriginalPrice = campaignOriginalPrice.price
            #print("status :", j.status)
            if j.status == "Pr_A_In" or j.status == "Pr_A_C":
                print("3333333333333333333333333333ActiveFound###########################")
                if "Active Campaigns" in campaign_status.keys():
                    campaign_status["Active Campaigns"].append(data)
                else:
                    campaign_status["Active Campaigns"] = [data]
            elif j.status == "Pr_P_C" and j.negoPrice == campaignOriginalPrice:
                if "New Requests" in campaign_status.keys():
                    campaign_status["New Requests"].append(data)
                else:
                    campaign_status["New Requests"] = [data]
            elif j.status == "Pr_P_C" and j.negoPrice != campaignOriginalPrice:
                if "Nego Requests" in campaign_status.keys():
                    campaign_status["Nego Requests"].append(data)
                else:
                    campaign_status["Nego Requests"] = [data]
            elif j.status == "Pr_P_In": #sponsor cannot do anything with these
                if "Pending Requests" in campaign_status.keys():
                    campaign_status["Pending Requests"].append(data)
                else:
                    campaign_status["Pending Requests"] = [data]
            elif j.status == "P_P_In":
                if "Public Requests" in campaign_status.keys():
                    campaign_status["Public Requests"].append(data)
                else:
                    campaign_status["Public Requests"] = [data]
            
    print("campaign Status : ", campaign_status, data)
    return render_template("sponsor-dashboard.html", username=username, campaign_status = campaign_status, sponsor_data = sponsor_data, formData = formData, campiagn_id = campaign_id, influencer_id = influencer_id)


@app.route('/sponsoracceptinginfluencer/<campaign_id>/<influencer_id>')
def sponsorAcceptingInfluencer(campaign_id = None, influencer_id = None):
    #print(campaign_id, len(campaign_id), type(campaign_id), len(campaign_id.strip))
    if campaign_id != "None" and influencer_id != "None":
        campaign_id = int(campaign_id.strip())
        influencer_id = str(influencer_id.strip())
    campaignlist = RequestsandStaus.query.filter_by(campaign_id = (campaign_id)).all()

    print(type(campaignlist[0].campaign_id), (campaign_id), len(influencer_id))


    if len(campaignlist) == 1:
        print(RequestsandStaus.query.filter_by(campaign_id = (campaign_id), influencer_id = (influencer_id)).first())

        RequestsandStaus.query.filter_by(campaign_id = (campaign_id), influencer_id = (influencer_id)).update({'status' : "Pr_A_C"})
    else:
        RequestsandStaus.query.filter_by(campaign_id = (campaign_id), influencer_id = '0').delete()
        RequestsandStaus.query.filter_by(campaign_id = (campaign_id), influencer_id = (influencer_id)).update({'status' : "Pr_A_C"})

        Campaigns.query.filter_by(campaign_id = (campaign_id)).update({'industry_type' : "Private"})
    db.session.commit()
    return redirect('/sponsorDashboard/None/None')

@app.route('/sponsorrejectininfluencer/<campaign_id>/<influencer_id>')
def sponsorRejectinInfluencer(campaign_id = None, influencer_id = None):
    if campaign_id != "None" and influencer_id != "None":
        campaign_id = int(campaign_id.strip())
        influencer_id = str(influencer_id.strip())
    campaignlist = RequestsandStaus.query.filter_by(campaign_id = (campaign_id)).all()

    print(type(campaignlist[0].campaign_id), (campaign_id), len(influencer_id))


    if len(campaignlist) == 1:
        print(RequestsandStaus.query.filter_by(campaign_id = (campaign_id), influencer_id = (influencer_id)).first())

        RequestsandStaus.query.filter_by(campaign_id = (campaign_id), influencer_id = (influencer_id)).delete()
    else:
        #RequestsandStaus.query.filter_by(campaign_id = (campaign_id), influencer_id = '0').delete()
        RequestsandStaus.query.filter_by(campaign_id = (campaign_id), influencer_id = (influencer_id)).delete()
        #Campaigns.query.filter_by(campaign_id = (campaign_id)).update({'status' : "Private"})
    db.session.commit()
    return redirect('/sponsorDashboard')

@app.route('/influencerDashboard/<campaign_id>',methods=["GET","POST"])
def influencerDashboard(campaign_id = None):
    if campaign_id != "None":
        campaign_id = int(campaign_id.strip())
    f = open("influencer.txt","r")
    username = f.read()
    username = json.loads(username)["username"]
    print(username)
    campaigns_data = {}
    campaign_status = {}
    formData = {}
    sponsor_data = {} # to display on dashboard
    
    #fetch first sponsor id to use id in other tables
    influencer_data = InfluencerCred.query.filter_by(username = username).first()
    influencer_id = influencer_data.id
    
    campaigns_data = RequestsandStaus.query.filter_by(influencer_id = influencer_id).all()
    
    #select list of campaign id and store them in campaign data
    for i in campaigns_data:
        #all campaigns referning to sponsor_id
        campaign = Campaigns.query.filter_by(campaign_id = i.campaign_id).first()
        sponsor = SponsorCred.query.filter_by(id = campaign.sponsor_id).first()
        
        view = ''
        data = {
            "influencer_id" : influencer_id,
            "campaign_id" : i.campaign_id,
            "campaign_name": campaign.campaign_name,
            "goals" : campaign.goals,
            "description" : campaign.description,
            "price" : campaign.price,
            "negoPrice" : i.negoPrice,
            "progress" : campaign.progress,
            "duration" : campaign.duration,
            "sponsor_id" : sponsor.id,
            "sponsor_name" : sponsor.username,
            "sponsor_ind_type" : sponsor.industry_type,
            "message" : i.message
        }

        #print(data)
        campaignOriginalPrice = Campaigns.query.filter_by(campaign_id = i.campaign_id).first()
        campaignOriginalPrice = campaignOriginalPrice.price
        

        #print("status :", j.status)
        if str(campaign_id) == str(data["campaign_id"]):
            formData = data
            print("qweqewrreqeqweqeqewweqweqe : ", formData, data)
            if i.status == "Pr_A_In" or i.status == "Pr_A_C":
                view = "Active Campaigns"
            elif i.status == "Pr_P_In" and i.negoPrice == campaignOriginalPrice:
                view = "New Requests"
            elif i.status == "Pr_P_In" and i.negoPrice != campaignOriginalPrice:
                view = "Nego Requests"
            elif i.status == "Pr_P_C":
                view = "Pending Requests"
            formData["view"] = view

        
        if i.status == "Pr_A_In" or i.status == "Pr_A_C":
            print("3333333333333333333333333333ActiveFound###########################")
            if "Active Campaigns" in campaign_status.keys():
                campaign_status["Active Campaigns"].append(data)
            else:
                campaign_status["Active Campaigns"] = [data]
        elif i.status == "Pr_P_In" and i.negoPrice == campaignOriginalPrice:
            if "New Requests" in campaign_status.keys():
                campaign_status["New Requests"].append(data)
            else:
                campaign_status["New Requests"] = [data]
        elif i.status == "Pr_P_In" and i.negoPrice != campaignOriginalPrice:
                if "Nego Requests" in campaign_status.keys():
                    campaign_status["Nego Requests"].append(data)
                else:
                    campaign_status["Nego Requests"] = [data]
        elif i.status == "Pr_P_C": #sponsor cannot do anything with these
            if "Pending Requests" in campaign_status.keys():
                campaign_status["Pending Requests"].append(data)
            else:
                campaign_status["Pending Requests"] = [data]
    
    print("campaign Status : ", campaign_status)
    if request.method == "GET":
        return render_template("influencer-dashboard.html", username=username, campaign_status = campaign_status, campaign_id = campaign_id, formData = formData)
@app.route('/adminDasboard/<campaign_id>')
def adminDasboard(campaign_id = None):
    active_Campagins = RequestsandStaus.query.filter_by(status = "Pr_A_In").all() + RequestsandStaus.query.filter_by(status = "Pr_A_C").all()
    print('admin activecampaigns', active_Campagins)
    l = []
    data ={}
    formData = {}
    for i in active_Campagins:
        campaign = Campaigns.query.filter_by(id = i.campaign_id).first()
        l.append({
            'Campaign name' : campaign.campaign_name,
            'campaign_id' : campaign.id,
            'Description ' : campaign.description,
            'Duration' : campaign.duration,
            "Price" : i.negoPrice,
            'Influencer Name' : InfluencerCred.query.filter_by(id = i.influencer_id).first().username
        })
    active_Campagins = l
    print('active campaigns 2 ', active_Campagins)
    public = RequestsandStaus.query.filter_by(status = "P_P_In").all()
    l = []
    for i in public:
        campaign = Campaigns.query.filter_by(id = i.campaign_id).first()
        l.append({
            'Campaign name' : campaign.campaign_name,
            'campaign_id' : campaign.id,
            'Description ' : campaign.description,
            'Duration' : campaign.duration,
            "Price" : campaign.price
        })
    public = l
    print('public campaigns ',public)
    flagged_campaigns = RequestsandStaus.query.filter_by(status = "P_F_In").all() + RequestsandStaus.query.filter_by(status = "Pr_F_In").all() + RequestsandStaus.query.filter_by(status = "Pr_F_C").all()
    l = []
    print("wewrwerwerwerw", flagged_campaigns)
    campaign_ids= []
    for i in flagged_campaigns:
        campaign = Campaigns.query.filter_by(id = i.campaign_id).first()
        
        if(campaign.id not in campaign_ids):
            l.append({
                'Campaign name' : campaign.campaign_name,
                'campaign_id' : campaign.id,
                'Description ' : campaign.description,
                'Duration' : campaign.duration,
                "Price" : campaign.price
            })
            campaign_ids.append(campaign.id)
    flagged_campaigns = l
    print("datatatataa")
    campaign = Campaigns.query.filter_by(id = campaign_id).first()
    if campaign:

        data = {
            'Active Campaigns' : active_Campagins,
            'Public Campaigns' : public,
            'flagged' : flagged_campaigns,
            'formData' : {
                        'Campaign Name' : campaign.campaign_name,
                        'Description' : campaign.description,
                        'Price' : campaign.price,
                        'Duration' : campaign.duration,
                        'campaign_id' : campaign_id
                    },
            'campaign_id' : campaign_id
        }
    else:
        data = {
            'Active Campaigns' : active_Campagins,
            'Public Campaigns' : public,
            'flagged' : flagged_campaigns,
            'campaign_id' : campaign_id
        }
    print('data ',data)
    return render_template('admin-dasboard.html', code = 0, data = data)

@app.route('/flagadmin/<campaign_id>')
def flagAdmin(campaign_id = None):
    campaign = RequestsandStaus.query.filter_by(campaign_id = campaign_id).all()
    for i in campaign:
        if i.status[:2] == "P_":
            RequestsandStaus.query.filter_by(campaign_id = campaign_id, influencer_id = i.influencer_id).update({'status' : "P_F_In"})
        else:
            if i.status[-1] == "n":
                RequestsandStaus.query.filter_by(campaign_id = campaign_id, influencer_id = i.influencer_id).update({'status' : "Pr_F_In"})
            else:
                RequestsandStaus.query.filter_by(campaign_id = campaign_id, influencer_id = i.influencer_id).update({'status' : "Pr_F_C"})
    db.session.commit()
    return redirect('/adminDasboard/None')


@app.route('/deleteadmin/<campaign_id>')
def deleteAdmin(campaign_id = None):
    campaign = RequestsandStaus.query.filter_by(campaign_id = campaign_id).all()
    for i in campaign:
        RequestsandStaus.query.filter_by(campaign_id = campaign_id, influencer_id = i.influencer_id).update({'status' : "Delete"})
    db.session.commit()
    return redirect('/adminDasboard/None')

@app.route('/findadmin/<campaign_id>/<page>')
def findadmin(campaign_id = None, page = None):
    campgin = RequestsandStaus.query.all()
    data = {
        "Public Campaigns" : [],
        "Active Campaigns" : [],
        "Private Campaigns" : [],
        "Deleted Campaigns" : []
    }
    popData = {}
    for i in campgin:
        if i.status == "Pr_A_In" or i.status == "Pr_A_C" or i.status == "Pr_P_In" or i.status == "Pr_P_C":
            cam_details = Campaigns.query.filter_by(id = i.campaign_id).first()
            in_details = InfluencerCred.query.filter_by(id = i.influencer_id).first()
            l = {
                "Campaign name" : cam_details.campaign_name,
                "campaign_id" : cam_details.campaign_id,
                "Influencer Name" : in_details.username,
                "Influencer Reach" : in_details.rech,
                "Campaign Description" : cam_details.description,
                "Nego Price" : i.negoPrice,
                "Original Price" : cam_details.price,
                "Goals" : cam_details.goals
            }
            if str(i.campaign_id) == str(campaign_id):
                popData = l
                popData['page'] = "detailed"
                print("Pop Data ", popData)
            print(popData)
            if i.status == "Pr_P_In" or i.status == "Pr_P_C":
                data["Private Campaigns"].append(l)
            else:
                data["Active Campaigns"].append(l)
        elif i.status == "Delete" or i.status == "P_P_In":
            cam_details = Campaigns.query.filter_by(id = i.campaign_id).first()
            l = {
                "Campaign name" : cam_details.campaign_name,
                "campaign_id" : cam_details.campaign_id,
                "Campaign Description" : cam_details.description,
                "Nego Price" : i.negoPrice,
                "Original Price" : cam_details.price,
                "Goals" : cam_details.goals
            }
            if str(i.campaign_id) == str(campaign_id):
                popData = l
                popData['page'] = "not detailed"
                print("Pop DataN ",popData)
            print(popData)
            if i.status == "Delete":
                data["Deleted Campaigns"].append(l)
            elif i.status == "P_P_In":
                data["Public Campaigns"].append(l)
            """elif "F" in i.status:
                data["Flagged Campaigns"].append()"""
    return render_template('findAdmin.html', data = data, popData = popData)
@app.route('/showSponsorCampaigns/<mess>/<visibility>',methods=["GET","POST"])
def showSponsorCampaigns(mess=None, visibility = 'None'):
    f = open("sponsor.txt","r")
    username = json.loads(f.read())["username"]
    f.close()

    campdict = {}
    sponsor_id = SponsorCred.query.filter_by(username = username).first().id
    #campaigns who belong to sponor id
    campaigns = Campaigns.query.filter_by(sponsor_id=sponsor_id).all()
    #print('Campaigns : ', campaigns)
    campaign_id = [i.campaign_id for i in campaigns] #all the campiagn ids registered by the sponsor
    #print('Campaign ids : ',campaign_id)
    for i in campaigns:
        for j in RequestsandStaus.query.filter_by(campaign_id = i.campaign_id).all():
            #print("Influencer Id : ",j.influencer_id)
            if (j.influencer_id == 0 or j.influencer_id == '0'):
                #print("Influencer 0")
                data = {
                    "campaign_id" : j.campaign_id,
                    'campaign_name' : i.campaign_name,
                    'campaign_description' : i.description,
                    'goals' : i.goals,
                    'duration' : i.duration,
                    'price' : i.price,
                    'negoPrice' : j.negoPrice,
                    'progress' : i.progress,
                    'influencer_id' : j.influencer_id,
                    'influencer_name' : None,
                    'influencer_reac' : None,
                    'influencer_bio' : None,
                    'message': j.message
                }
            else:
                influencer = InfluencerCred.query.filter_by(id = j.influencer_id).first()
                data = {
                    "campaign_id" : j.campaign_id,
                    'campaign_name' : i.campaign_name,
                    'campaign_description' : i.description,
                    'goals' : i.goals,
                    'duration' : i.duration,
                    'price' : i.price,
                    'negoPrice' : j.negoPrice,
                    'progress' : i.progress,
                    'influencer_id' : j.influencer_id,
                    'influencer_name' : influencer.username,
                    'influencer_reac' : influencer.rech,
                    'influencer_bio' : influencer.bio,
                    'message': j.message
                }
            
            
            #print("jjjjjjjjjjjjjjj",j.status)
            if j.status =="Pr_C_In":
                if "Completed Campaigns" in campdict.keys():
                    campdict['Completed Campaigns'].append(data)
                else:
                    campdict["Completed Campaigns"] = [data]
            elif j.status[0:4] == "Pr_A":
                if "Accepted Campaigns" in campdict.keys():
                    campdict['Accepted Campaigns'].append(data)
                else:
                    campdict["Accepted Campaigns"] = [data]
            elif j.influencer_id == '0':
                #print('public adde ', data, j.influencer_id)
                if "Public Campaigns" in campdict.keys():
                    campdict['Public Campaigns'].append(data)
                else:
                    campdict["Public Campaigns"] = [data]
            elif j.status[0:2] == "Pr":
                if "Private Campaigns" in campdict.keys():
                    campdict['Private Campaigns'].append(data)
                else:
                    campdict["Private Campaigns"] = [data]
    #print("campdict :", campdict)
    influencers =  InfluencerCred.query.all()
    #print("influencers : ", influencers)
    if influencers:
        influencer_ids = [i.id for i in influencers]
    else:
        influencer_ids = []

    if request.method == "GET":
        return render_template("show-sponsor-campaigns.html", data = campdict, mess = mess, showForm = visibility, influencers = influencers)
    elif request.method == "POST":
        campaign_name = request.form["campaign_name"]
        description = request.form["description"]
        price = int(request.form["price"])
        duration = int(request.form["duration"])
        in_id = int(request.form["re_to_in"])
        goals = int(request.form["goals"])
        print("in_id",in_id)
        if in_id in influencer_ids or in_id == 0:
            
            count = len(Campaigns.query.all())+1
            print(count)
            if in_id == 0:
                c = Campaigns(campaign_name = campaign_name, campaign_id=str(count), sponsor_id = int(sponsor_id), price = price, progress = 0, description=description, duration = duration, industry_type = 'Public', goals = goals)
                d = RequestsandStaus(influencer_id = in_id, campaign_id = str(count), status = "P_P_In", message = None, negoPrice = price)
            else:
                c = Campaigns(campaign_name = campaign_name, campaign_id=str(count), sponsor_id = sponsor_id, price = price, progress = 0, description=description, duration = duration, industry_type = 'Private', goals = goals)
                d = RequestsandStaus(influencer_id = in_id, campaign_id = str(count), status = "Pr_P_In", message = None, negoPrice = price)
            #print(c)
            db.session.add(c)
            db.session.add(d)
            print("campaign added")
            db.session.commit()

        else:
            return redirect('/showSponsorCampaigns/"No such influencer"/None')
        return redirect('/showSponsorCampaigns/None/None')
@app.route('/influenceracceptingsponsor/<campaign_id>/<influencer_id>')
def InfluencerAcceptSponsor(campaign_id = None, influencer_id = None):
    if campaign_id != "None" and influencer_id != "None":
        campaign_id = int(campaign_id.strip())
        influencer_id = str(influencer_id.strip())
    campaignlist = RequestsandStaus.query.filter_by(campaign_id = (campaign_id)).all()

    print(type(campaignlist[0].campaign_id), (campaign_id), len(influencer_id))


    if len(campaignlist) == 1:
        print(RequestsandStaus.query.filter_by(campaign_id = (campaign_id), influencer_id = (influencer_id)).first())

        RequestsandStaus.query.filter_by(campaign_id = (campaign_id), influencer_id = (influencer_id)).update({'status' : "Pr_A_In"})
    else:
        RequestsandStaus.query.filter_by(campaign_id = (campaign_id), influencer_id = '0').delete()
        RequestsandStaus.query.filter_by(campaign_id = (campaign_id), influencer_id = (influencer_id)).update({'status' : "Pr_A_In"})
        Campaigns.query.filter_by(campaign_id = (campaign_id)).update({'status' : "Private"})
    db.session.commit()
    return redirect('/influencerDashboard/None')

@app.route('/influencerrejectinsponsor/<campaign_id>/<influencer_id>')
def InfluencerRejectSponsor(campaign_id = None, influencer_id = None):
    if campaign_id != "None" and influencer_id != "None":
        campaign_id = int(campaign_id.strip())
        influencer_id = str(influencer_id.strip())
    campaignlist = RequestsandStaus.query.filter_by(campaign_id = (campaign_id)).all()

    print(type(campaignlist[0].campaign_id), (campaign_id), len(influencer_id))


    if len(campaignlist) == 1:
        print(RequestsandStaus.query.filter_by(campaign_id = (campaign_id), influencer_id = (influencer_id)).first())

        RequestsandStaus.query.filter_by(campaign_id = (campaign_id), influencer_id = (influencer_id)).delete()
    else:
        #RequestsandStaus.query.filter_by(campaign_id = (campaign_id), influencer_id = '0').delete()
        RequestsandStaus.query.filter_by(campaign_id = (campaign_id), influencer_id = (influencer_id)).delete()
        #Campaigns.query.filter_by(campaign_id = (campaign_id)).update({'status' : "Private"})
    db.session.commit()
    return redirect('/influencerDashboard/None')

@app.route('/sponsornegoinfluencer/<campaign_id>/<influencer_id>', methods=["GET", "POST"])
def sponsorNegoSponsor(campaign_id = None, influencer_id = None):
    message = request.form["message"]
    print("message : ", message)
    negoPrice = request.form["negoPrice"]
    RequestsandStaus.query.filter_by(campaign_id = campaign_id, influencer_id = influencer_id).update({'status' : "Pr_P_In", 'message' : message, 'negoPrice' : negoPrice})
    db.session.commit()
    return redirect('/sponsorDashboard/None/None')
@app.route('/influencerrequestsponsor/<campaign_id>', methods=["GET", "POST"])
def influencerRequestSponsor(campaign_id = None):
    f = open("influencer.txt","r")
    username = json.loads(f.read())["username"]
    f.close()
    influencer_id = InfluencerCred.query.filter_by(username = username).first().id
    if request.method == "GET":
        l = RequestsandStaus(campaign_id = campaign_id, influencer_id = influencer_id, status = "Pr_P_C", message=None, negoPrice = Campaigns.query.filter_by(campaign_id = campaign_id).first().price)
        db.session.add(l)
        db.session.commit()
    else:
        #condition left if the form is blank
        message = request.form["message"]
        print("message : ", message)
        negoPrice = request.form["negoPrice"]
        if RequestsandStaus.query.filter_by(campaign_id = campaign_id, influencer_id = influencer_id).first():
            print('werw')
            RequestsandStaus.query.filter_by(campaign_id = campaign_id, influencer_id = influencer_id).update({'status' : "Pr_P_C", 'message' : message, 'negoPrice' : negoPrice})
            db.session.commit()
            return redirect('/influencerDashboard/None')
        else:
            print('trrtrtr')
            l = RequestsandStaus(campaign_id = (campaign_id), influencer_id = (influencer_id), status = "Pr_P_C", message=message, negoPrice = negoPrice)
            db.session.add(l)
            db.session.commit()
    return redirect('/findcampaigns/None')

@app.route('/findcampaigns/<campaign_id>')
def findCampaigns(campaign_id = None):
    campaigns = Campaigns.query.filter_by(industry_type = "Public").all()
    f = open("influencer.txt","r")
    username = json.loads(f.read())["username"]
    f.close()
    c = []
    formData = {}
    influencer_id = InfluencerCred.query.filter_by(username = username).first().id
    if campaign_id != 'None':
        campaign = Campaigns.query.filter_by(campaign_id = campaign_id).first()
        
        formData =  {
            "campaign_name" : campaign.campaign_name,
            "campaign_description" : campaign.description,
            "duration" : campaign.duration,
            "price" : campaign.price,
            "goals" : campaign.goals,
            "sponsor_name" : SponsorCred.query.filter_by(id = campaign.sponsor_id).first().username,
            "influencer_id" : influencer_id
        }
    
    for i in campaigns:
        if len(RequestsandStaus.query.filter_by(campaign_id = i.campaign_id, influencer_id = influencer_id).all()) == 0:
            c.append(i)
    return render_template('findcampaigns.html', campaigns = c, campaign_id = campaign_id, formData = formData)
@app.route('/stat/<code>')
def stat(code = None):
    matplotlib.use('Agg')
    plt.figure(2)
    plt.rcParams["figure.figsize"] = [7.00, 3.50]
    plt.rcParams["figure.autolayout"] = True
    # Plot the histogram
    l = RequestsandStaus.query.all()
    n = {}
    for i in l:
        if i.status in n:
            n[i.status]+= 1
        else:
            n[i.status] = 1
    l = n
    plt.pie(n.values(), labels = n.keys())

  
    # Save the histogram
    plt.savefig('code/static/campaign_industry_type.png')
    plt.figure(1)
    plt.rcParams["figure.figsize"] = [7.00, 3.50]
    plt.rcParams["figure.autolayout"] = True
    # Plot the histogram
    j = SponsorCred.query.all()
    n = {}
    for i in j:
        if i.industry_type in n:
            n[i.industry_type] = n[i.industry_type]+1
        else:
            n[i.industry_type] = 1
    j = n
    plt.hist(n)
    plt.savefig('code/static/sponsor_industry_type.png')
    return render_template('stat.html', code = code)
#Rg Page 
@app.route("/", methods=["GET","POST"]) #default page
@app.route("/sponsorRg/<code>", methods=["GET","POST"])
def sponsorRg(code = 0):
    return render_template("sponsor-rg.html",code = code)
@app.route('/influencer-rg/<code>', methods=["GET","POST"])
def influencerRg(code = 0):
    return render_template("influencer-rg.html",code = code)

#Ln Page
@app.route('/sponsorLn/<code>', methods=["GET", "POST"])
def sponsorLn(code = 0):
    return render_template("sponsor-ln.html", code= code)

@app.route('/influencerLn/<code>', methods=["GET", "POST"])
def influencerLn(code = 0):
    return render_template("influencer-ln.html", code= code)

@app.route('/adminLn/<code>')
def adminLn(code = 0):
    return render_template('admin-ln.html', code = code)

#Check if the user reg detials valid or not and then store them in database
@app.post('/checkandrgsponsor')
def CheckandRgSponsor():
    username = request.form['username']
    pasword = request.form['pasword']
    ind_type = request.form['industry-type']
    budget = request.form["budget"]
    if pasword and username and ind_type and budget:
        try:
            user = SponsorCred(username=username,pasword=pasword, industry_type = ind_type, budget = budget)
            print('Sponser stored in var')
            db.session.add(user)
            print('sponsor added in session')
            db.session.commit()
            print("sponsor commit")
            with open('sponsor.txt', 'wb') as f:
                json.dump({'username': username}, codecs.getwriter('utf-8')(f), ensure_ascii=False)
            return redirect("/sponsorDashboard/None/None")
        except IntegrityError as error:
            print(error)
            return redirect("/sponsorRg/2")
        except Exception as err:
            print(err)
            return redirect("/sponsorRg/2")
    return redirect("/sponsorRg/1")

@app.route('/checkandlnsponsor', methods=["POST"])
def CheckandLnSponsor():
    username = request.form['username']
    pasword = request.form['pasword']
    if username:
        if pasword:
            user = SponsorCred.query.filter_by(username=username).first()
            if not user:
                return redirect("/sponsorLn/3") #'No such Username exists'
            dbname= user.username
            dbpswd = user.pasword
            if pasword == dbpswd:
                with open('sponsor.txt', 'wb') as f:
                    json.dump({'username': username}, codecs.getwriter('utf-8')(f), ensure_ascii=False)
                return redirect("/sponsorDashboard/None/None")
            else:
                return redirect('/sponsorLn/4') #"Password is wrong"
        return redirect("/sponsorLn/2") #'Pasword field is empty'
    return redirect("/sponsorLn/1") #Username field is empty

#influencer
@app.route('/checkandrginfluencer', methods=["POST"])
def CheckandRgInfluencer():
    username = request.form['username']
    pasword = request.form['pasword']
    reac = request.form['reac']
    bio = request.form['bio']
    if pasword and username and reac and bio:
        try:
            user = InfluencerCred(username=username,pasword=pasword, rech = reac, bio = bio)
            print('Influencer stored in var')
            db.session.add(user)
            print('sponsor added in session')
            db.session.commit()
            print("influencer commit")
            with open('influencer.txt', 'wb') as f:
                json.dump({'username': username}, codecs.getwriter('utf-8')(f), ensure_ascii=False)
            return redirect('/influencerDashboard/None')
        except IntegrityError as error:
            print(error)
            return redirect('/influencer-rg/2')
    return redirect('/influencer-rg/1')

@app.post('/checkandlninfluencer')
def CheckandLnInfluencer():
    username = request.form['username']
    pasword = request.form['pasword']
    if username:
        if pasword:
            user = InfluencerCred.query.filter_by(username=username).first()
            if not user:
                return redirect('/influencerLn/3') #"No such Username exists"
            dbname= user.username
            dbpswd = user.pasword
            if pasword == dbpswd:
                with open('influencer.txt', 'wb') as f:
                    json.dump({'username': username}, codecs.getwriter('utf-8')(f), ensure_ascii=False)
                return redirect('/influencerDashboard/None')
            else:
                return redirect('/influencerLn/3') #"Password is wrong"
        return redirect('/influencerLn/2') #"Pasword field is empty"
    return redirect("/influencerLn/1") #'Username field is empty'

@app.route('/checkandlnadmin/', methods=["GET", "POST"])
def loginadmin():
    username = request.form["username"]
    pasword = request.form["pasword"]
    if username:
        if pasword:
            user = AdminCred.query.filter_by(username=username).first()
            if not user:
                return redirect('/adminLn/3') #username does not exist
            dbname= user.username
            dbpswd = user.pasword
            if pasword == dbpswd:
                with open('admin.txt', 'wb') as f:
                    json.dump({'username': username}, codecs.getwriter('utf-8')(f), ensure_ascii=False)
                return redirect('/adminDasboard/None')
            else:
                return redirect('/adminLn/4') #passwod is wroing
        return redirect('/adminLn/2') #Pasword field is empty
    return redirect("/adminLn/1") #Username field is empty

app.run(debug=True)