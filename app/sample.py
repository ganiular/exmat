def find_x4_payee(user_id, part_id, level, paytype, cur):
    print_color(f"x4 got {dict(user_id=user_id, part_id=part_id, level=level, paytype=cd.pt(paytype, cur))}",200,255,255)

    if not user_id:
        return user_id, part_id, paytype

    matrix = cd.get_x4matrix(user_id, level, cur)

    if not matrix:
        cd.add_miss_payment(user_id, part_id, 2, level, paytype, 1, cur)
        print_color(f"missed payment: {dict(payee=user_id, payer=part_id, matrix='x4', level=level, paytype=cd.pt(paytype, cur), reason=cd.rs(1, cur))}", 255,180,180)

        if paytype == 1:
            paytype = 2
        return find_x4_payee(cd.get_sponsor_id(user_id, index, cur), part_id, level, paytype, cur)

    if paytype == 7:
        if(matrix['debt'] >= 4):
            cd.add_miss_payment(user_id, part_id, 2, level, paytype, 4)
            print_color(f"missed payment: {dict(payee=user_id, payer=part_id, matrix='x4', level=level, paytype=cd.pt(paytype, cur), reason=cd.rs(4, cur))}", 255,180,180)            
            return find_x4_payee(matrix['upline'], part_id, level, 8, cur)
        elif matrix['f_slot_count'] == 0:
            make_f_slot_count(matrix['id'], cur)
            cd.add_slot(user_id, part_id, 2, level, 1, paytype, cur)
            print_color(f"slot filled: {dict(owner=user_id, filler=part_id, matrix='x4', level=level, position=1, paytype=cd.pt(paytype, cur))}", 255,180,180)

            cd.set_payindex(matrix['id'], 2, cur)
            if matrix["debt"] > 0:
                cd.set_debt(matrix['id'], matrix['debt'] - 1, cur)
            return find_x4_payee(matrix['upline'], part_id, level, 8, cur)
        elif matrix['s_slot_count'] == 3:
            cd.add_slot(user_id, part_id, 1, level, 3, paytype, cur)
            print_color(f"slot filled: {dict(owner=user_id, filler=part_id, matrix='x3', level=level, position=3, paytype=cd.pt(paytype, cur))}", 255,180,180)
            print_color(f"reinvestemt: {dict(user_id=user_id, matrix='x3', level=level, count=matrix['reopen_count']+1)}", 255,150)

            # if matrix is not full and has reached MAX_REOPEN
            if matrix["reopen_count"] + 1 >= current_app.config['MAX_REOPEN'] and  \
            and matrix["account_index"] < spon_count:
                print_color("current account full, switching to the next account")
                print_color(f"account switched: {dict(user_id=user_id, sponsor_id={}, matrix='x3', level=level, count=matrix['account_index'] + 1)}", 100,200,255)

                cd.remove_x4matrix(matrix["id"], cur)
                cd.set_x4(user_id, level, matrix['account_index']+1, matrix['last_sponsor_index'],
                    matrix['next_partner_index'], matrix['debt'], matrix['payindex'], cur)
                print_color(f"removed matrix: {dict((x,matrix[x]) for x in matrix.keys())}")

                if level in (0,1):
                    return find_x4_payee(cd.get_sponsor_id(user_id, 0, cur), user_id, level, 4, cur)
                else:
                    return find_x4_payee(cd.get_sponsor_id(user_id, matrix['account_index'], cur), user_id, level, 1, cur)

            cd.set_debt_and_reopen(matrix["id"], matrix["debt"] + 1, cur)
            return find_x4_payee(matrix['upline'], user_id, level, 3, cur)
        else:
            cd.add_slot(user_id, part_id, 2, level, matrix['s_slot_count'] + 3, paytype, cur)
            cd.make_s_slot_count(matrix['id'], cur)
            print_color(f"slot filled: {dict(owner=user_id, filler=part_id, matrix='x4', level=level, position=matrix['s_slot_count'] + 3, paytype=cd.pt(paytype, cur))}", 255,180,180)
            
            if is_offline_user(user_id, cur):
                cd.add_miss_payment(user_id, part_id, 1, level, paytype, 2, cur)
                print_color(f"missed payment: {dict(payee=user_id, payer=part_id, matrix='x3', level=level, paytype=cd.pt(paytype, cur), reason=cd.rs(2, cur))}", 255,180,180)
                return find_x4_payee(matrix['upline'], user_id, level, 9, cur)
            elif matrix["reopen_count"] >= current_app.config['MAX_REOPEN']:
                cd.add_miss_payment(user_id, part_id, 1, level, paytype, 3, cur)
                print_color(f"missed payment: {dict(payee=user_id, payer=part_id, matrix='x3', level=level, paytype=cd.pt(paytype, cur), reason=cd.rs(2, cur))}", 255,180,180)
                return find_x4_payee(matrix['upline'], user_id, level, 9, cur)
            else:
                cd.set_debt(matrix['id'], matrix['debt'] + 1, cur)
                return user_id, part_id, paytype
    elif paytype in (1,2):
        cd.add_x4matrix(part_id, user_id, level, cur)
    
    if matrix['payindex'] < 3:
        if matrix['f_slot_count'] < 2:
            cd.add_slot(user_id, part_id, 2, level, matrix['f_slot_count'] + 1, paytype, cur)
            cd.make_f_slot_count(matrix['id'], cur)
            print_color(f"slot filled: {dict(owner=user_id, filler=part_id, matrix='x4', level=level, position=matrix['f_slot_count'] + 1, paytype=cd.pt(paytype, cur))}", 255,180,180)
        if matrix['debt'] > 0:
            cd.set_debt(matrix['id'], matrix['debt'] - 1, cur)
        cd.set_payindex(matrix['id'], matrix['payindex'] + 1, cur)
        if matrix["reopen_count"] >= current_app.config['MAX_REOPEN']:
            lsi = matrix['last_sponsor_index']
            if lsi+ 1 < spon_count: lsi += 1
            else: lsi = -1

            cd.set_x3_last_sponsor_index_and_reopen(matrix['id'], lsi, cur)
            return find_x4_payee(cd.get_sponsor_id(user_id, lsi if lsi>=0 else 0, cur), user_id, level, 5, cur)
        else:
            return find_x4_payee(matrix['upline'], part_id, level, 8, cur)
    elif matrix['s_slot_count'] == 3 and matrix['payindex'] % 3 == 0:
        cd.add_slot(user_id, part_id, 2, level, 6, paytype, cur)
        print_color(f"slot filled: {dict(owner=user_id, filler=part_id, matrix='x4', level=level, position=6, paytype=cd.pt(paytype, cur))}", 255,180,180)
        print_color(f"reinvestemt: {dict(user_id=user_id, matrix='x3', level=level, count=matrix['reopen_count']+1)}", 255,150)

        if ((matrix['account_index']+1) * (matrix['reopen_count']+1)) // (spon_count * current_app.config['MAX_REOPEN']) > 0  \
            and matrix["account_index"] + 1 >= spon_count:
            print_color("all account full, payment to the next sponsor")
            lsi = matrix['last_sponsor_index']
            if lsi+ 1 < spon_count: lsi += 1
            else: lsi = -1

            cd.set_x3_last_sponsor_index_and_reopen(matrix['id'], lsi, cur)

            return find_x4_payee(cd.get_sponsor_id(user_id, lsi if lsi>=0 else 0, cur), user_id, level, 5, cur)
        elif (matrix['reopen_count'] + 1) >= current_app.config['MAX_REOPEN']:
            print_color("current account full, switching to the next account")
            (f"account switched: {dict(user_id=user_id, sponsor_id={}, matrix='x3', level=level, count=matrix['account_index'] + 1)}", 100,200,255)

            cd.remove_x4matrix(matrix["id"], cur)
            cd.set_x3(user_id, level, matrix['account_index']+1, matrix['last_sponsor_index'], matrix['next_partner_index'], cur)
            print_color(f"removed matrix: {dict((x,matrix[x]) for x in matrix.keys())}")

            assert cur.lastrowid != 0, "could not remove matrix"

            if level in (0,1):
                return find_x4_payee(cd.get_sponsor_id(user_id, 0, cur), user_id, level, 4, cur)
            else:
                return find_x4_payee(cd.get_sponsor_id(user_id, index, cur), user_id, level, 1, cur)
        else:
            cd.make_x3_reopen_count(matrix["id"], cur)
            return find_x3_payee(cd.get_sponsor_id(user_id, matrix['account_index'], cur), user_id, level, 3, cur)
    elif matrix['payindex'] % 3 == 0:
        cd.set_payindex(matrix['id'], matrix['payindex'] + 1, cur)
        cd.add_slot(user_id, part_id, 2, level, matrix['s_slot_count'] + 3, paytype, cur)
        cd.make_s_slot_count(matrix['id'], cur)
        print_color(f"slot filled: {dict(owner=user_id, filler=part_id, matrix='x4', level=level, position=matrix['s_slot_count'] + 3, paytype=cd.pt(paytype, cur))}", 255,180,180)
        
        downline_matrix = cd.get_x4_downline_matrix(matrix['id'])
        
        if downline_matrix:
            if downline_matrix['debt'] < 4 and downline_matrix['f_slot_count'] < 3:
                cd.make_f_slot_count(downline_matrix['id'], cur)
                cd.add_slot(downline_matrix['owner'], part_id, 2, level, downline_matrix['f_slot_count'] + 1, paytype, cur)
                print_color(f"slot filled: {dict(owner=user_id, filler=part_id, matrix='x4', level=level, position=downline_matrix['f_slot_count']+1, paytype=cd.pt(paytype, cur))}", 255,180,180)
        if cd.is_offline_user(user_id, cur):
            cd.add_miss_payment(user_id, part_id, 2, level, paytype, 2 cur)
            print_color(f"missed payment: {dict(payee=user_id, payer=part_id, matrix='x4', level=level, paytype=cd.pt(paytype, cur), reason=cd.rs(2, cur))}", 255,180,180)
            
            npi = matrix['next_partner_index']
            downline, npi = cd.get_next_downline(user_id, 1, level, npi, cur)
            cd.set_x4_next_partner_index(matrix['id'], npi+1, cur)

            return find_x4_payee(downline, user_id, level, 6, cur)
        elif matrix['reopen_count'] >= current_app.config['MAX_REOPEN']:
            cd.add_miss_payment(user_id, part_id, 2, level, paytype, 3 cur)
            print_color(f"missed payment: {dict(payee=user_id, payer=part_id, matrix='x4', level=level, paytype=cd.pt(paytype, cur), reason=cd.rs(3, cur))}", 255,180,180)

            downline_matrix = cd.get_x4_downline_matrix(matrix['id'])
            return find_x4_payee(downline_matrix["owner"] if downline_matrix else 0, user_id, level, 6, cur)
        else:
            return user_id, part_id, paytype
    else:
        cd.set_payindex(matrix['id'], matrix['payindex'] + 1, cur)
        downline_matrix = cd.get_x4_downline_matrix(matrix['id'])
        return find_x4_payee(downline_matrix["owner"] if downline_matrix else 0, part_id, level, 7, cur)




def find_x3_payee(user_id, part_id, level, paytype, cur):
    print_color(f"got {dict(user_id=user_id, part_id=part_id, level=level, paytype=cd.pt(paytype, cur))}",200,255,255)

    if not user_id:
        return user_id, part_id, paytype

# 	slot_count = cd.get_slot_count(user_id, 1, level, cur)
# 	index = (slot_count+1) // (3 * current_app.config['MAX_REOPEN'])
    matrix = cd.get_x3matrix(user_id, level, cur)

    if not matrix:
        cd.add_miss_payment(user_id, part_id, 1, level, paytype, 1, cur)
        print_color(f"missed payment: {dict(payee=user_id, payer=part_id, matrix='x3', level=level, paytype=cd.pt(paytype, cur), reason=cd.rs(1, cur))}", 255,180,180)

        if paytype == 1:
            paytype = 2
        return find_x3_payee(cd.get_sponsor_id(user_id, 0, cur), part_id, level, paytype, cur)
    if paytype in (1,2):
        cd.add_x3matrix(part_id, user_id, level, cur)

    spon_count = cd.get_sponsor_count(user_id, cur)
    print_color(f"user matrix: {dict((x,matrix[x]) for x in matrix.keys())}", 255,180,10)

    # check for reopen
    if matrix['slot_count'] == 2:
        cd.add_slot(user_id, part_id, 1, level, 3, paytype, cur)
        print_color(f"slot filled: {dict(owner=user_id, filler=part_id, matrix='x3', level=level, position=3, paytype=cd.pt(paytype, cur))}", 255,180,180)
        print_color(f"reinvestemt: {dict(user_id=user_id, matrix='x3', level=level, count=matrix['reopen_count']+1)}", 255,150)

        # check if all accounts are full
        #if matrix['account_index'] + 1 == spon_count and matrix['reopen_count'] + 1 >= current_app.config['MAX_REOPEN']:
        if ((matrix['account_index']+1) * (matrix['reopen_count']+1)) // (spon_count * current_app.config['MAX_REOPEN']) > 0  \
            and matrix["account_index"] + 1 >= spon_count:
            print_color("all account full, payment to the next sponsor")
            lsi = matrix['last_sponsor_index']
            if lsi+ 1 < spon_count: lsi += 1
            else: lsi = -1

            cd.set_x3_last_sponsor_index_and_reopen(matrix['id'], lsi, cur)

            return find_x3_payee(cd.get_sponsor_id(user_id, lsi if lsi>=0 else 0, cur), user_id, level, 5, cur)
        # check if current account is full
        #elif ((slot_count+1) % (3 * current_app.config['MAX_REOPEN'])) == 0:
        #elifprint_color (matrix['reopen_count'] + 1) % current_app.config['MAX_REOPEN'] == 0:
        elif (matrix['reopen_count'] + 1) >= current_app.config['MAX_REOPEN']:
            print_color("current account full, switching to the next account")
            (f"account switched: {dict(user_id=user_id, sponsor_id={}, matrix='x3', level=level, count=matrix['account_index'] + 1)}", 100,200,255)

            cd.remove_x3matrix(matrix["id"], cur)
            cd.set_x3(user_id, level, matrix['account_index']+1, matrix['last_sponsor_index'], matrix['next_partner_index'], cur)
            print_color(f"removed matrix: {dict((x,matrix[x]) for x in matrix.keys())}")

            assert cur.lastrowid != 0, "could not remove matrix"

            if level in (0,1):
                return find_x3_payee(cd.get_sponsor_id(user_id, 0, cur), user_id, level, 4, cur)
            else:
                return find_x3_payee(cd.get_sponsor_id(user_id, index, cur), user_id, level, 1, cur)
        else:
            cd.make_x3_reopen_count(matrix["id"], cur)
            return find_x3_payee(cd.get_sponsor_id(user_id, matrix['account_index'], cur), user_id, level, 3, cur)

    cd.add_slot(user_id, part_id, 1, level, matrix['slot_count']+1, paytype, cur)
    cd.make_x3_slot_count(matrix['id'], cur)
    print_color(f"slot filled: {dict(owner=user_id, filler=part_id, matrix='x3', level=level, position=matrix['slot_count']+1, paytype=cd.pt(paytype, cur))}", 255,180,180)

    if cd.is_offline_user(user_id, cur):
        cd.add_miss_payment(user_id, part_id, 1, level, paytype, 2, cur)
        print_color(f"missed payment: {dict(payee=user_id, payer=part_id, matrix='x3', level=level, paytype=cd.pt(paytype, cur), reason=cd.rs(2, cur))}", 255,180,180)

        npi = matrix['next_partner_index']
        downline, npi = cd.get_next_downline(user_id, 1, level, npi, cur)

        cd.set_x3_next_partner_index(matrix['id'], npi+1, cur)
        return find_x3_payee(downline, user_id, level, 6, cur)
    # if all account is full
    #if matrix['account_index'] + 1 >= spon_count and matrix['reopen_count'] >= current_app.config['MAX_REOPEN']:
    if matrix['reopen_count'] >= current_app.config['MAX_REOPEN']:
        print_color("all account full, payment to the next downline")
        cd.add_miss_payment(user_id, part_id, 1, level, paytype, 3, cur)
        print_color(f"missed payment: {dict(payee=user_id, payer=part_id, matrix='x3', level=level, paytype=cd.pt(paytype, cur), reason=cd.rs(3, cur))}", 255,180,180)

        npi = matrix['next_partner_index']
        downline, npi = cd.get_next_downline(user_id, 1, level, npi, cur)

        cd.set_x3_next_partner_index(matrix['id'], npi+1, cur)
        return find_x3_payee(downline, user_id, level, 6, cur)
    return user_id, part_id, paytype
