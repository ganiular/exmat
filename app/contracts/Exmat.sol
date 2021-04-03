pragma solidity ^0.5.14;

import "./ITRC20.sol";

contract Exmat{
    uint8 public constant ACTIVE_PERIOD = 40;
    uint8 public constant MAX_REOPEN = 5;
    uint8 public constant MAX_LEVEL = 15;
    uint public constant MIN_PRICE = 2_500_000; // 2.5TRCT
    
    uint constant MAX4 = 36**4;
    uint constant MAX5 = 36**5;
    uint constant MAX6 = 36**6;
    uint constant MAX = MAX4 + MAX5 + MAX6;
    bytes constant cypher = "ADPRFQ9XMJUS46HKYT7I3GLBCOV012Z8EN5W";
    
    address constant root = 0x4362B59BfE02A335Fc736cE0D59eAcE4C292563b;
    uint public partnersCount;
    mapping(address => User) users;
    mapping(string => address) public idToAddress;
    
    // TRCT address on shasta is 0xE6Cc08181fa7175a33f536F16112fB11bb4c9291
    // USDJ address on nile is 0x70082243784dcdf3042034E7B044d6D342A91360
    
    ITRC20 constant trc = ITRC20(0xE6Cc08181fa7175a33f536F16112fB11bb4c9291);
    
    struct User {
        uint8 active_payment_since_last_login;
        uint partnersCount;
        uint lastLogin;
        string id;
        address[] sponsors;
        mapping(uint8 => X3Matrix) x3Matrices;
        mapping(uint8 => X4Matrix) x4Matrices;
    }
    struct X3Matrix{
        bool activated;
        uint currentAccount;
        uint reopenCount;
        uint index;
        uint partnerIndex;
        uint sponsorIndex;
        uint partnersCount;
        uint slots;
        address[] partners;
        address[] uplines;
    }
    struct X4Matrix {
        bool activated;
        uint8 debt;
        uint8 payIndex;
        uint _i;
        uint currentAccount;
        uint reopenCount;
        uint index;
        uint partnerIndex;
        uint sponsorIndex;
        uint partnersCount;
        uint firstSlots;
        uint secondSlots;
        address[] partners;
        mapping(uint => address) uplines;
    }

    function generateId(uint n) public pure returns(string memory id) {
        require(n >= 0 && n < MAX, "Out of range");
        uint i1;
        uint i2;
        uint i3;
        uint i4;
        if(n < MAX4) {
            n = (n / 32) + (MAX4/32 * (n % 32));
            uint m = (n%35) % 4;
            (i3, i4) = (n/36, n%36);
            (i2, i3) = (i3/36, i3%36);
            (i1, i2) = (i2/36, i2%36);
            if(m == 1)
                return string( abi.encodePacked(cypher[i1], cypher[i2], cypher[i3], cypher[i4]));
            if(m == 3)
                return string( abi.encodePacked(cypher[i2], cypher[i3], cypher[i4], cypher[i1]));
            if(m == 0)
                return string( abi.encodePacked(cypher[i3], cypher[i4], cypher[i1], cypher[i2]));
            
                return string( abi.encodePacked(cypher[i4], cypher[i1], cypher[i2], cypher[i3]));
        }
        n -= MAX4;
        if (n < MAX5){
            n = (n / 32) + (MAX5/32 * (n % 32));
            uint i5;
            uint m = (n%35) % 5;
            (i4, i5) = (n/36, n%36);
            (i3, i4) = (i4/36, i4%36);
            (i2, i3) = (i3/36, i3%36);
            (i1, i2) = (i2/36, i2%36);
            if(m == 4)
                return string( abi.encodePacked(cypher[i1], cypher[i2], cypher[i3], cypher[i4], cypher[i5]));
            if(m == 1)
                return string( abi.encodePacked(cypher[i2], cypher[i3], cypher[i4], cypher[i5], cypher[i1]));
            if(m == 2)
                return string( abi.encodePacked(cypher[i3], cypher[i4], cypher[i5], cypher[i1], cypher[i2]));
            if(m == 0)
                return string( abi.encodePacked(cypher[i4], cypher[i5], cypher[i1], cypher[i2], cypher[i3]));
            
                return string( abi.encodePacked(cypher[i5], cypher[i1], cypher[i2], cypher[i3], cypher[i4]));
        }
        n -= MAX5;
        if(n < MAX6){
            n = (n / 32) + (MAX6/32 * (n % 32));
            uint i5;
            uint i6;
            uint m = (n%35) % 6;
            (i5, i6) = (n/36, n%36);
            (i4, i5) = (i5/36, i5%36);
            (i3, i4) = (i4/36, i4%36);
            (i2, i3) = (i3/36, i3%36);
            (i1, i2) = (i2/36, i2%36);
            if(m == 5)
                return string( abi.encodePacked(cypher[i1], cypher[i2], cypher[i3], cypher[i4], cypher[i5], cypher[i6]));
            if(m == 2)
                return string( abi.encodePacked(cypher[i2], cypher[i3], cypher[i4], cypher[i5], cypher[i6], cypher[i1]));
            if(m == 1)
                return string( abi.encodePacked(cypher[i3], cypher[i4], cypher[i5], cypher[i6], cypher[i1], cypher[i2]));
            if(m == 4)
                return string( abi.encodePacked(cypher[i4], cypher[i5], cypher[i6], cypher[i1], cypher[i2], cypher[i3]));
            if(m == 3)
                return string( abi.encodePacked(cypher[i5], cypher[i6], cypher[i1], cypher[i2], cypher[i3], cypher[i4]));
            
                return string( abi.encodePacked(cypher[i6], cypher[i1], cypher[i2], cypher[i3], cypher[i4], cypher[i5]));
        }
    }
    ///////////////////////////////////////////////////////////////////////////////
    /*                             User                                        */
    ///////////////////////////////////////////////////////////////////////////////
    function isOffline(User memory self) private view returns (bool) {
        return (now - self.lastLogin) > (ACTIVE_PERIOD * 1 days) && self.active_payment_since_last_login > 2;
    }
    ///////////////////////////////////////////////////////////////////////////////
    /*                              X3Matrix                                  */
    ///////////////////////////////////////////////////////////////////////////////
    function isFull(X3Matrix memory self, User memory owner) private pure returns(bool) {
        return (self.reopenCount >= MAX_REOPEN) && (self.currentAccount + 1 == owner.sponsors.length);
    }
    function addPartner(X3Matrix storage self, address partner) private returns(uint) {
        self.partners.push(partner);
        ++ self.partnersCount;
        return self.partners.length - 1;
    }
    function removePartner(X3Matrix storage self, X3Matrix storage partner) private {
        delete self.partners[partner.index];
        -- self.partnersCount ;
    }
    function getNextPartner(X3Matrix storage self) private returns (address partner) {
        if(self.partnersCount == 0) return address(0);
        while(true) {
            if(self.partnerIndex == self.partners.length){
                self.partnerIndex = 0;
            }
            partner = self.partners[self.partnerIndex];
            ++self.partnerIndex;
            if( partner == address(0)) continue;
            return partner;
        }
    }
    function getSponsor(X3Matrix memory self, User storage owner) private view returns (address) {
        return owner.sponsors[self.currentAccount];
    }
    function getNextSponsor(X3Matrix storage self, User storage owner) private returns (address sponsor) {
        if (self.sponsorIndex == owner.sponsors.length) self.sponsorIndex = 0;
        sponsor = owner.sponsors[self.sponsorIndex];
        self.sponsorIndex += 1;
        return sponsor;
    }
    function reopen(X3Matrix storage self, User storage owner) private returns (uint) {
        delete self.slots;
        self.reopenCount += 1;
        if (! isFull(self, owner) && self.reopenCount >= MAX_REOPEN) {
            self.currentAccount += 1;
            self.reopenCount = 0;
        }
        return self.reopenCount;
    }
    ///////////////////////////////////////////////////////////////////////////////
    /*                              X4Matrix                                  */
    ///////////////////////////////////////////////////////////////////////////////
    function isFull(X4Matrix storage self, User storage owner) private view returns(bool) {
        return (self.reopenCount >= MAX_REOPEN) && (self.currentAccount + 1 == owner.sponsors.length);
    }
    function addPartner(X4Matrix storage self, address partner) private returns(uint) {
        self.partners.push(partner);
        ++ self.partnersCount;
        return self.partners.length - 1;
    }
    function removePartner(X4Matrix storage self, X4Matrix storage other) private {
        delete self.partners[other.index];
        -- self.partnersCount ;
    }
    function getNextPartner1(X4Matrix storage self) private returns (address partner) {
        if(self.partnersCount == 0) return address(0);
        while(true) {
            if(self.partnerIndex == self.partners.length){
                self.partnerIndex = 0;
            }
            partner = self.partners[self.partnerIndex];
            ++self.partnerIndex;
            if( partner == address(0)) continue;
            return partner;
        }
    }
    function getNextPartner2(X4Matrix storage self) private returns (address partner) {
        if (self.partnersCount == 0){
            return address(0);
        }
        while(true){
            if(self._i / 3 >= self.partners.length) {
                self._i = 0;
            }
            partner = self.partners[self._i / 3];
            if (partner == address(0) && self._i % 3 == 0){
                if((self._i += 3) >= self.partners.length) {
                    self._i = 0;
                }
                continue;
            }
            ++self._i;
            return partner;
        }
    }
    function getSponsor(X4Matrix memory self, User memory owner) private pure returns (address) {
        return owner.sponsors[self.currentAccount];
    }
    function getNextSponsor(X4Matrix storage self, User storage owner) private returns (address sponsor) {
        if (self.sponsorIndex == owner.sponsors.length) self.sponsorIndex = 0;
        sponsor = owner.sponsors[self.sponsorIndex];
        ++self.sponsorIndex;
        return sponsor;
    }
    function reopen(X4Matrix storage self, User storage owner) private returns (uint) {
        delete self.firstSlots;
        delete self.secondSlots;
        self.payIndex = 1;
        self.reopenCount += 1;
        if (! isFull(self, owner) && self.reopenCount >= MAX_REOPEN) {
            self.currentAccount += 1;
            self.reopenCount = 0;
        }
        return self.reopenCount;
    }
    ///////////////////////////////////////////////////////////////////////////////
    /*                             Exmat Events                                  */
    ///////////////////////////////////////////////////////////////////////////////
    event Registration(address indexed userAddress, address indexed sponsorAddress, string userId);
    event AddAccount(address indexed user, address indexed sponsor, uint count);
    event Paid(address indexed payee, address indexed payer, uint8 matrix, uint8 level, uint8 paytype);
    event MissPayment(address indexed payee, address indexed payer, uint8 matrix, uint8 level, uint8 paytype, uint8 reason);
    // event Reinvest(address indexed user, uint8 matrix, uint8 level, uint count);
    // event LevelFull(address indexed user, uint8 matrix, uint8 level);
    // event SwitchAccount(address indexed user, address indexed sponsor, uint8 matrix, uint8 level, uint count);
    event SlotFilled(address indexed user, address indexed filler, uint8 matrix, uint8 level, uint position, uint8 filltype);
    event Upgrade(address indexed user, address beneficiary, uint8 matrix, uint8 level);
    event Login(address indexed user, uint date);
    ///////////////////////////////////////////////////////////////////////////////
    /*                             Exmat Methods                                 */
    ///////////////////////////////////////////////////////////////////////////////
    function register(address sponsorAddress) public {
        User storage user = users[msg.sender];
        require(user.sponsors.length == 0, "Already registered");
        User storage sponsor = users[sponsorAddress];
        require(sponsor.sponsors.length != 0, "Sponsor not registered");
        require(msg.sender != sponsorAddress, "Self referral is not allowed");
        // require(trc.balanceOf(msg.sender) >= MIN_PRICE*2, "Insufficient balance, 5 USDT is required");
        
        
        user.id = generateId(partnersCount++);
        user.lastLogin = now;
        idToAddress[user.id] = msg.sender;
        
        ++ sponsor.partnersCount;
        user.sponsors.push(sponsorAddress);
        
        emit Registration(msg.sender, sponsorAddress, user.id);
        
        buyMatrix(1, 1);
        buyMatrix(2, 1);
    }
    function buyMatrix(uint8 matrix, uint8 level) public {
        User storage user = users[msg.sender];
        require(user.sponsors.length != 0, "You have not registered");
        require(level > 0 && level <= MAX_LEVEL && matrix > 0 && matrix < 3, "Invalid input");

        uint price = MIN_PRICE * 2 ** (uint(level) - 1);
        // require(trc.balanceOf(msg.sender) >= price, "Insufficient balance");
        if (matrix == 1){
            if(level > 1){
                require(user.x3Matrices[level - 1].activated, "Previous level should be activated");
            }
            X3Matrix storage mat = user.x3Matrices[level];
            require(mat.activated == false, "Level already activated");
            //require(msg.value >= price, "Invalid price");
            
            address sponsorAddress = getSponsor(mat, user);
            
            (address payeeAddress, address payerAddress, uint8 paytype) = 
            findX3Payee(sponsorAddress, msg.sender, level, 1);
            
            if (payeeAddress == address(0)) payeeAddress = root;
            else ++users[payeeAddress].active_payment_since_last_login; 
            
            bool success = trc.transferFrom(msg.sender, payeeAddress, price);
            
            require(success, "Payment error");
            
            mat.activated = true;
            emit Paid(payeeAddress, payerAddress, 1, level, paytype);
            emit Upgrade(msg.sender, payeeAddress, 1, level);
        }
        else if( matrix == 2){
            if(level > 1){
                require(user.x4Matrices[level - 1].activated, "Previous level should be activated");
                // price = MIN_PRICE * 2 ** (uint(level) - 1);
            }
            X4Matrix storage mat = user.x4Matrices[level];
            require(mat.activated == false, "Level already activated");

            address sponsorAddress = getSponsor(mat, user);
            
            (address payeeAddress, address payerAddress, uint8 paytype) = 
            findX4Payee(sponsorAddress, msg.sender, level, 1);
            
            if (payeeAddress == address(0)) payeeAddress = root;
            else ++users[payeeAddress].active_payment_since_last_login;
            
            bool success = trc.transferFrom(msg.sender, payeeAddress, price);

            require(success, "Payment error");
            
            mat.activated = true;
            emit Paid(payeeAddress, payerAddress, 2, level, paytype);
            emit Upgrade(msg.sender, payeeAddress, 2, level);
        }
    }
    function addAccount(address sponsorAddress) public {
        User storage user = users[msg.sender];
        require(user.sponsors.length != 0, "You have not registered");
        User storage sponsor = users[sponsorAddress];
        require(sponsor.sponsors.length != 0, "Sponsor not registered");
        require(msg.sender != sponsorAddress, "Self referral is not allowed");
        // require(user.x3Matrices[2].activated && user.x4Matrices[2].activated, "You must upgrade both matrices to level 2 first");
        // require(sponsor.x3Matrices[1].activated && sponsor.x4Matrices[1].activated, "Sponsor have not upgrade both matrices to level 1");
        // require(msg.value >= price, "Invalid price");
        for(uint i; i < user.sponsors.length; i++){
            require(sponsorAddress != user.sponsors[i], "You've already used this sponsor");
        }
        uint price = MIN_PRICE * 2;
        // require(trc.balanceOf(msg.sender) >= price, "Insufficient balance");
        
        emit AddAccount(msg.sender, sponsorAddress, user.sponsors.length);
        
        (address payeeAddress, address payerAddress, uint8 paytype) = 
        findX3Payee(sponsorAddress, msg.sender, 1, 1);
        
        if (payeeAddress == address(0)) payeeAddress = root;
        else ++users[payeeAddress].active_payment_since_last_login;
        // if( !payeeAddress.send(price) ){
        //     payeeAddress.transfer(price);
        // }
        bool success;
        success = trc.transferFrom(msg.sender, payeeAddress, price);
            
        require(success, "Payment error");
        
        emit Paid(payeeAddress, payerAddress, 1, 1, paytype);
        
        (payeeAddress, payerAddress, paytype) = 
        findX4Payee(sponsorAddress, msg.sender, 1, 1);
        
        if (payeeAddress == address(0)) payeeAddress = root;
        else ++users[payeeAddress].active_payment_since_last_login;
        // if( !payeeAddress.send(price) ){
        //     payeeAddress.transfer(price);
        // }
        success = trc.transferFrom(msg.sender, payeeAddress, price);
            
        require(success, "Payment error");
        
        emit Paid(payeeAddress, payerAddress, 2, 1, paytype);

        user.sponsors.push(sponsorAddress);
        ++ sponsor.partnersCount;
    }
    function findX3Payee(address userAddress, address partnerAddress, uint8 level, uint8 paytype)
    private returns (address, address, uint8) {
        while(true){
            if (userAddress == address(0)){
                return (address(uint160(userAddress)), partnerAddress, paytype);
            }
            
            User storage user = users[userAddress];
            User storage partner = users[partnerAddress];
            X3Matrix storage mat = user.x3Matrices[level];
            
            if(!mat.activated){
                emit MissPayment(userAddress, partnerAddress, 1, level, paytype, 1);
                
                if (paytype == 1){
                    paytype = 2;
                }
                userAddress = getSponsor(mat, user);
                continue;
            }
            
            if(paytype == 1 || paytype == 2){
                X3Matrix storage partnerMat = partner.x3Matrices[level];
                partnerMat.index = addPartner(mat, partnerAddress);
                partnerMat.uplines.push(userAddress);
            }
            
            if (mat.slots == 2) {
                uint count = reopen(mat, user);
                
                emit SlotFilled(userAddress, partnerAddress, 1, level, 3, paytype);
                // emit Reinvest(userAddress, 1, level, count);
                // if (count == MAX_REOPEN){
                //     emit LevelFull(userAddress, 1, level);
                // }
                if (count == 0){
                    address uplineAddress = mat.uplines[mat.currentAccount - 1];
                    removePartner(users[uplineAddress].x3Matrices[level], mat);
                    // emit SwitchAccount(userAddress, getSponsor(mat, user), 1, level, mat.currentAccount + 1);
                    
                    if (level == 1){
                        partnerAddress = userAddress;
                        userAddress = user.sponsors[0];
                        paytype = 4;
                    }
                    else{
                        partnerAddress = userAddress;
                        userAddress = getSponsor(mat, user);
                        paytype = 1;
                    }
                    continue;
                }
                if (isFull(mat, user)){
                    partnerAddress = userAddress;
                    userAddress = getNextSponsor(mat, user);
                    paytype = 5;
                    continue;
                }
                partnerAddress = userAddress;
                userAddress = getSponsor(mat, user);
                paytype = 3;
                continue;
            }
            else{
                ++mat.slots;
                emit SlotFilled(userAddress, partnerAddress, 1, level, mat.slots, paytype);
                
                if (isOffline(user)){
                    emit MissPayment(userAddress, partnerAddress, 1, level, paytype, 2);
                    partnerAddress = userAddress;
                    userAddress = getNextPartner(mat);
                    paytype = 6;
                    continue;
                }
                else if( isFull(mat, user)){
                    emit MissPayment(userAddress, partnerAddress, 1, level, paytype, 3);
                    partnerAddress = userAddress;
                    userAddress = getNextPartner(mat);
                    paytype = 6;
                    continue;
                }
                return (address(uint160(userAddress)), partnerAddress, paytype);
            }
        }
    }
    function findX4Payee(address userAddress, address partnerAddress, uint8 level, uint8 paytype)
    private returns (address, address, uint8) {
        while(true) {
            if (userAddress == address(0)){
                return (address(uint160(userAddress)), partnerAddress, paytype);
            }
            
            User storage user = users[userAddress];
            User storage partner = users[partnerAddress];
            X4Matrix storage mat = user.x4Matrices[level];
            
            if(!mat.activated){
                emit MissPayment(userAddress, partnerAddress, 2, level, paytype, 1);
                
                if (paytype == 1){
                    paytype = 2;
                }
                userAddress = getSponsor(mat, user);
                continue;
            }
            
            if (paytype == 7){
                if(mat.debt >= 4){
                    emit MissPayment(userAddress, partnerAddress, 2, level, paytype, 4);
                    userAddress = mat.uplines[mat.currentAccount];
                    paytype = 8;
                    continue;
                }
                else if(mat.firstSlots == 0){
                    ++mat.firstSlots;

                    emit SlotFilled(userAddress, partnerAddress, 2, level, 1, paytype);

                    mat.payIndex = 2;
                    if (mat.debt > 0){
                        mat.debt -= 1;
                    }
                    userAddress = mat.uplines[mat.currentAccount];
                    paytype = 8;
                    continue;
                }
                else if(mat.secondSlots == 3){
                    mat.debt += 1;
                    uint count = reopen(mat, user);
                    emit SlotFilled(userAddress, partnerAddress, 2, level, 6, paytype);
                    // emit Reinvest(userAddress, 2, level, count);

                    // if (count == MAX_REOPEN){
                    //     emit LevelFull(userAddress, 2, level);
                    // }
                    if( count == 0 ){
                        address uplineAddress = mat.uplines[mat.currentAccount - 1];
                        removePartner(users[uplineAddress].x4Matrices[level], mat);
                        
                        // emit SwitchAccount(userAddress, getSponsor(mat, user), 2, level, mat.currentAccount + 1);
                        if(level == 1){
                            partnerAddress = userAddress;
                            userAddress = user.sponsors[0];
                            paytype = 4;
                            continue;
                        }
                        else{
                            partnerAddress = userAddress;
                            userAddress = getSponsor(mat, user);
                            paytype = 1;
                            continue;
                        }
                    }
                    else{
                        partnerAddress = userAddress;
                        userAddress = mat.uplines[mat.currentAccount];
                        paytype = 3;
                        continue;
                    }
                }
                else{
                    ++mat.secondSlots;
                    emit SlotFilled(userAddress, partnerAddress, 2, level, mat.secondSlots + 2, paytype);
                    
                    if(isOffline(user)){
                        emit MissPayment(userAddress, partnerAddress, 2, level, paytype, 2);
                        partnerAddress = userAddress;
                        userAddress = mat.uplines[mat.currentAccount];
                        paytype = 9;
                        continue;
                    }
                    else if(isFull(mat, user)){
                        emit MissPayment(userAddress, partnerAddress, 2, level, paytype, 3);
                        partnerAddress = userAddress;
                        userAddress = mat.uplines[mat.currentAccount];
                        paytype = 9;
                        continue;
                    }
                    mat.debt += 1;
                    return (address(uint160(userAddress)), partnerAddress, paytype);
                }
            }
            if (paytype == 1 || paytype == 2){
                X3Matrix storage partnerMat = partner.x3Matrices[level];
                partnerMat.index = addPartner(mat, partnerAddress);
                partnerMat.uplines.push(userAddress);
            }

            if (mat.payIndex < 3){
                if (mat.firstSlots < 2){
                    ++mat.firstSlots;
                    emit SlotFilled(userAddress, partnerAddress, 2, level, mat.firstSlots, paytype);
                }
                if(mat.debt > 0){
                    mat.debt -= 1;
                }
                mat.payIndex += 1;
                if (isFull(mat, user)){
                    partnerAddress = userAddress;
                    userAddress = getNextSponsor(mat, user);
                    paytype = 5;
                    continue;
                }
                userAddress = mat.uplines[mat.currentAccount];
                paytype = 8;
                continue;
            }
            else if(mat.secondSlots == 3 && mat.payIndex % 3 == 0){
                uint count = reopen(mat, user);
                emit SlotFilled(userAddress, partnerAddress, 2, level, 6, paytype);
                // emit Reinvest(userAddress, 2, level, count);

                // if (count == MAX_REOPEN){
                //      emit LevelFull(userAddress, 2, level);
                // }
                if( count == 0){
                    address uplineAddress = mat.uplines[mat.currentAccount - 1];
                    removePartner(users[uplineAddress].x4Matrices[level], mat);
                    // emit SwitchAccount(userAddress, getSponsor(mat, user), 2, level, mat.currentAccount + 1);

                    if(level == 1){
                        partnerAddress = userAddress;
                        userAddress = user.sponsors[0];
                        paytype = 4;
                        continue;
                    }
                    partnerAddress = userAddress;
                    userAddress = getSponsor(mat, user);
                    paytype = 1;
                    continue;
                }
                if (isFull(mat, user)){
                    partnerAddress = userAddress;
                    userAddress = getNextSponsor(mat, user);
                    paytype = 5;
                    continue;
                }
                partnerAddress = userAddress;
                userAddress = getSponsor(mat, user);
                paytype = 3;
                continue;
            }
            else if(mat.payIndex % 3 == 0){
                mat.payIndex += 1;
                ++mat.secondSlots;
                emit SlotFilled(userAddress, partnerAddress, 2, level, mat.secondSlots + 2, paytype);

                address nextPartnerAddress = getNextPartner2(mat);
                if (nextPartnerAddress != address(0)){
                    X4Matrix storage npmat = users[nextPartnerAddress].x4Matrices[level];
                    if (npmat.debt < 4 && npmat.firstSlots < 3){
                        ++npmat.firstSlots;
                        emit SlotFilled(nextPartnerAddress, partnerAddress, 2, level, npmat.firstSlots, paytype);
                    }
                }
                if(isOffline(user)){
                    emit MissPayment(userAddress, partnerAddress, 2, level, paytype, 2);
                    partnerAddress = userAddress;
                    userAddress = getNextPartner1(mat);
                    paytype = 6;
                    continue;
                }
                else if(isFull(mat, user)){
                    emit MissPayment(userAddress, partnerAddress, 2, level, paytype, 3);
                    partnerAddress = userAddress;
                    userAddress = getNextPartner2(mat);
                    paytype = 6;
                    continue;
                }
                return (address(uint160(userAddress)), partnerAddress, paytype);
            }
            else{
                mat.payIndex += 1;
                userAddress = getNextPartner2(mat);
                paytype = 7;
                continue;
            }
        }
    }
    function addressToId(address userAddress) public view returns (string memory id) {
        return users[userAddress].id;
    }
    function getUser(address userAddress) public view returns(
        uint partnerCount, 
        uint active_payment_since_last_login, 
        uint lastLogin, 
        address[] memory sponsors) {
        User memory user = users[userAddress];
        return (
            user.partnersCount,
            user.active_payment_since_last_login,
            user.lastLogin,
            user.sponsors
        );
    }
    function getX3Matrix(address userAddress, uint8 level) public view returns(
        bool activated, 
        uint currentAccount, 
        uint reopenCount, 
        uint slots) {
        X3Matrix memory mat = users[userAddress].x3Matrices[level];
        return (
            mat.activated,
            mat.currentAccount,
            mat.reopenCount,
            mat.slots
            );
    }
    function getX4Matrix(address userAddress, uint8 level) public view returns(
        bool activated, 
        uint currentAccount, 
        uint reopenCount, 
        uint firstSlots, 
        uint secondSlots) {
        X4Matrix memory mat = users[userAddress].x4Matrices[level];
        return (
            mat.activated,
            mat.currentAccount + 1,
            mat.reopenCount,
            mat.firstSlots,
            mat.secondSlots
            );
    }
    ///////////////////////////////////////////////////////////////////////////////
    /* in future i should remove destruction and write bytesToAddress
      function in another library */
    ///////////////////////////////////////////////////////////////////////////////
    modifier onlyCreator{
        require(msg.sender == root);
        _;
    }
    function () external {
        if(msg.data.length == 0) {
            return register(root);
        }
        
        register(bytesToAddress(msg.data));
    }
    function destruction() public onlyCreator {
        selfdestruct(address(uint160(root)));
    }
    function withdraw(address _to, uint amount) public onlyCreator {
        address(uint160(_to)).transfer(amount);
    }
    function bytesToAddress(bytes memory bys) private pure returns (address addr) {
        assembly {
            addr := mload(add(bys, 20))
        }
    }
    constructor() public {
        User storage user = users[root];
        user.id = generateId(partnersCount++);
        user.lastLogin = now;
        user.sponsors.push(address(0));
        idToAddress[user.id] = root;
        
        for(uint8 level=1; level <= MAX_LEVEL; level++){
            user.x3Matrices[level].activated = true;
            X4Matrix storage x4 = user.x4Matrices[level];
            x4.activated = true;
            x4.payIndex = 1;
        }
    }
    function activate() external {
        User storage user = users[msg.sender];
        require(user.sponsors.length != 0, "Unknown user");
        user.lastLogin = now;
        user.active_payment_since_last_login = 0;
        
        emit Login(msg.sender, user.lastLogin);
    }
}
