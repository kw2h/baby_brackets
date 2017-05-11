from .models import *
from math import ceil

def get_nameids(match_id, size):
    ''' Return input id of teams playing each other in the first round as a
        tuple given a match_id and bracket size
    '''
    dict16 = {1:(1,13), 2:(2,14), 3:(3,15), 4:(4,16), 5:(5,9), 6:(6,10), 7:(7,11), 8:(8,12)}
    dict32 = {1:(1,13), 2:(2,14), 3:(3,15), 4:(4,16), 5:(5,9), 6:(6,10), 7:(7,11), 8:(8,12)}
    dict64 = {1:(1,13), 2:(2,14), 3:(3,15), 4:(4,16), 5:(5,9), 6:(6,10), 7:(7,11), 8:(8,12)}
    size_dict = {16:dict16, 32:dict32, 64:dict64}
    return size_dict[size][match_id]

def get_region(match_id):
    ''' Return region given match_id '''
    if match_id in (1,5):
        return 'a -east'
    elif match_id in (2,6):
        return 'b - west'
    elif match_id in (3,7):
        return 'c - midwest'
    else:
        return 'd - south'

def parentBracketMaker(bracket_id, size, form, db):
    ''' Create the Matchups for a bracket given dict of inputs from form. Form
        inputs are used to create names which are then assigned to first round
        Matchups. Matchups in rounds > 1 are created without name1 or name2
        assigned.
    '''
    for i in range(1, size/2 + 1):
        region = get_region(i)
        nm1_id,nm2_id = get_nameids(i, size) # get mapping from form input to match_id
        name1 = form['name'+str(nm1_id)]
        name2 = form['name'+str(nm2_id)]
        nm1 = Names(name=name1, seed=int(ceil(nm1_id/4.0))) # create new name records in db
        nm2 = Names(name=name2, seed=int(ceil(nm2_id/4.0))) # create new name records in db
        db.session.add(nm1)
        db.session.add(nm2)
        db.session.commit()
        m = Matchups(bracket_id=bracket_id,match_id=i,name1_id=nm1.id,
                     name2_id=nm2.id, region=region, rnd=1) # create matchup
        db.session.add(m)
        db.session.commit()

    if size == 16:
        match1 = Matchups(bracket_id=bracket_id, match_id=9, region='a - east', rnd=2)
        match2 = Matchups(bracket_id=bracket_id, match_id=10, region='b - west', rnd=2)
        match3 = Matchups(bracket_id=bracket_id, match_id=11, region='c - midwest', rnd=2)
        match4 = Matchups(bracket_id=bracket_id, match_id=12, region='d - south', rnd=2)
        match5 = Matchups(bracket_id=bracket_id, match_id=13, region='a - final4', rnd=3)
        match6 = Matchups(bracket_id=bracket_id, match_id=14, region='b - final4', rnd=3)
        match7 = Matchups(bracket_id=bracket_id, match_id=15, region='championship', rnd=4)

        db.session.add(match1)
        db.session.add(match2)
        db.session.add(match3)
        db.session.add(match4)
        db.session.add(match5)
        db.session.add(match6)
        db.session.add(match7)

    db.session.commit()

def userBracketMaker(refer_bracket_id, user_bracket_id, db):
    ''' Duplicate all the Matchups in refer_bracket_id with bracket_id
        replaced with user_bracket_id and no winners set
    '''
    parent_matchups = Matchups.query.filter_by(bracket_id=refer_bracket_id).all()
    for m in parent_matchups:
        if m.rnd == 1:
            m = Matchups(bracket_id=user_bracket_id, match_id=m.match_id,
                         name1_id=m.name1_id, name2_id=m.name2_id, region=m.region,
                         rnd=m.rnd)
        else:
            m = Matchups(bracket_id=user_bracket_id, match_id=m.match_id,
                          region=m.region, rnd=m.rnd)
        db.session.add(m)
        db.session.commit()

def scoreBracket(bracket_id):
     b = Bracket.query.filter_by(id=bracket_id).first()
     m = Matchupsc.query.filter_by(bracket_id=bracket_id).all()
