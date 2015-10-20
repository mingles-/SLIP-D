//
// Created by Sam Davies on 20/10/2015.
// Copyright (c) 2015 Sam Davies. All rights reserved.
//

import XCTest
import Locksmith
@testable import SmartLock

class LocksmithTest: XCTestCase {

    override func setUp() {
        super.setUp()
        // Put setup code here. This LocksmithSmartLockthod is called before the invocation of each test LocksmithSmartLockthod in the class.
    }

    override func tearDown() {
        // Put teardown code here. This LocksmithSmartLockthod is called after the invocation of each test LocksmithSmartLockthod in the class.
        super.tearDown()
    }

    func testGetAuthKey() {
        do {
            try Locksmith.saveData(["auth": "hello"], forUserAccount: "token")
        } catch {}
        do {
            try Locksmith.updateData(["auth": "hello"], forUserAccount: "token")
        } catch {}
        let dictionary = Locksmith.loadDataForUserAccount("token")
        let tokenObject: AnyObject = dictionary!["auth"]!
        let token: String = tokenObject as! String
        XCTAssert(token == "hello", "Pass")
    }

    /* Ensure that the userPass exists */
    func testSaveGetUserPass(){
        LocksmithSmartLock.saveUserPass("user", pass: "pass")
        let (user, pass, found) = LocksmithSmartLock.getUserPass()
        XCTAssert(user == "user")
        XCTAssert(pass == "pass")
    }
}

