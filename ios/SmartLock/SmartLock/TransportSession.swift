//
// Created by Sam Davies on 10/10/2015.
// Copyright (c) 2015 Sam Davies. All rights reserved.
//

import Foundation
import Alamofire
import SwiftyJSON
import Locksmith
import PromiseKit

class TransportSession: TransportSessionProtocol {
    
    var tokenRequested: Bool = false
    var url: String = ""
    var method: Alamofire.Method = Alamofire.Method.GET
    var parameters: Dictionary<String, String> = Dictionary<String, String>()
    var returnsMultiJson: Bool = true
    
    var completion: (response: NSHTTPURLResponse, json: SwiftyJSON.JSON) -> Void = {(response: NSHTTPURLResponse, json: SwiftyJSON.JSON) in}
    var loginRedirect: () -> Void = {}

    private var username = ""
    private var password = ""
    
    func basicRequestPromise() -> Promise<SwiftyJSON.JSON> {
//        let (user, pass, found) = LocksmithThing.getUserPass()
//        if (found) {
//            self.username = user
//            self.password = pass
//        }

        return Promise { fulfill, reject in
            // alamofire code that calls either fill or reject
            Alamofire.request(self.method, Settings.API_URL + self.url, parameters: self.parameters)
                .authenticate(user: self.username, password: self.password)
                .responseJSON { response in
                    switch response.result {
                    case .Success(let data):
                        // if the json is multi dimentioal, we must convert it to UTF-8 encoding,
                        // if it isn't then we can't
                        if let dataString: String = data as? String {
                            let multiData = dataString.dataUsingEncoding(NSUTF8StringEncoding)!
                            let json = SwiftyJSON.JSON(data: multiData)
                            fulfill(json)
                        }else{
                            let json = SwiftyJSON.JSON(data)
                            fulfill(json)
                        }
                    case .Failure(let error):
                        print("Request failed with error: \(error)")
                        reject(error)
                    }
            }
        }
    }
    
    private func processResponseData(data: AnyObject, response: NSHTTPURLResponse){
        // if the json is multi dimentioal, we must convert it to UTF-8 encoding,
        // if it isn't then we can't
        if let dataString: String = data as? String {
            let multiData = dataString.dataUsingEncoding(NSUTF8StringEncoding)!
            let json = SwiftyJSON.JSON(data: multiData)
            self.completion(response: response, json: json)
        }else{
            let json = SwiftyJSON.JSON(data)
            self.completion(response: response, json: json)
        }
    }
}
