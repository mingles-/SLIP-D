//
// Created by Sam Davies on 20/10/2015.
// Copyright (c) 2015 Sam Davies. All rights reserved.
//

import Foundation
import SwiftyJSON
import Alamofire
import Locksmith
import PromiseKit

struct LocksmithSmartLock {

    static func getUserPass() -> (String, String, Bool){
        let dictionary = Locksmith.loadDataForUserAccount("userPass")

        if let dictionary = dictionary,
        userObject: AnyObject = dictionary["user"],
        user: String = userObject as? String,
        passObject: AnyObject = dictionary["pass"],
        pass: String = passObject as? String {
            return (user, pass, true)
        } else {
            return ("", "", false)
        }
    }

    static func saveUserPass(user: String, pass: String) {
        let data = ["user": user, "pass": pass]
        do {
            try Locksmith.updateData(data, forUserAccount: "userPass")
        } catch {}
    }

    static func deleteUserPass() {
        do {
            try Locksmith.deleteDataForUserAccount("userPass")
        } catch {}
    }
}