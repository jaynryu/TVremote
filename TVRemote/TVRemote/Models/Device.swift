import Foundation

struct Device: Identifiable, Codable {
    let id: String
    let name: String
    let address: String
}

struct DevicesResponse: Codable {
    let devices: [Device]
}

struct PairResponse: Codable {
    let deviceProvidesPin: Bool?
    let message: String?
    let paired: Bool?

    enum CodingKeys: String, CodingKey {
        case deviceProvidesPin = "device_provides_pin"
        case message
        case paired
    }
}

struct CommandResponse: Codable {
    let status: String
    let command: String?
    let text: String?
}

struct StatusResponse: Codable {
    let connected: Bool
    let deviceId: String?
    let app: String?
    let title: String?
    let artist: String?
    let mediaType: String?
    let deviceState: String?
    let error: String?

    enum CodingKeys: String, CodingKey {
        case connected
        case deviceId = "device_id"
        case app, title, artist
        case mediaType = "media_type"
        case deviceState = "device_state"
        case error
    }
}
