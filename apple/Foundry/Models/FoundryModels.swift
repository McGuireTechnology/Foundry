import Foundation

struct HealthResponse: Decodable {
    let status: String
}

struct TokenPair: Decodable {
    let accessToken: String
    let refreshToken: String

    enum CodingKeys: String, CodingKey {
        case accessToken = "access_token"
        case refreshToken = "refresh_token"
    }
}

struct VortexUser: Decodable, Identifiable {
    let id: String
    let email: String
    let isActive: Bool

    enum CodingKeys: String, CodingKey {
        case id
        case email
        case isActive = "is_active"
    }
}

struct ForgotPasswordResponse: Decodable {
    let message: String
    let resetToken: String?

    enum CodingKeys: String, CodingKey {
        case message
        case resetToken = "reset_token"
    }
}

struct MessageResponse: Decodable {
    let message: String
}

struct APIErrorEnvelope: Decodable {
    let detail: String
}
