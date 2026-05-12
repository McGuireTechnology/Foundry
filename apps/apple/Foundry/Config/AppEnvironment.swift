import Foundation

enum FoundryRuntimeEnvironment: String, CaseIterable {
    case local
    case staging
    case production

    static let defaultValue: FoundryRuntimeEnvironment = .local

    static func resolve(from rawValue: String?) -> FoundryRuntimeEnvironment {
        guard let rawValue else {
            return defaultValue
        }

        let normalized = rawValue.trimmingCharacters(in: .whitespacesAndNewlines).lowercased()
        switch normalized {
        case "local":
            return .local
        case "staging":
            return .staging
        case "production", "prod":
            return .production
        default:
            return defaultValue
        }
    }
}

struct AppEnvironment {
    static let defaultLocalBaseURL = "http://localhost:8000"
    static let defaultAPIVersion = "v1"

    let runtimeEnvironment: FoundryRuntimeEnvironment
    let baseURL: URL
    let apiVersion: String

    static let current = AppEnvironment.makeCurrent()

    private static func makeCurrent() -> AppEnvironment {
        let runtimeEnvironment = FoundryRuntimeEnvironment.resolve(from: processOrInfoValue(for: "FOUNDRY_APP_ENV"))
        let legacyBaseURLValue = processOrInfoValue(for: "FOUNDRY_API_BASE_URL")
        let defaultLocalURL = parseBaseURL(defaultLocalBaseURL) ?? URL(string: defaultLocalBaseURL)!

        let localURL = parseBaseURL(processOrInfoValue(for: "FOUNDRY_API_BASE_URL_LOCAL")) ??
            parseBaseURL(legacyBaseURLValue) ??
            defaultLocalURL
        let stagingURL = parseBaseURL(processOrInfoValue(for: "FOUNDRY_API_BASE_URL_STAGING")) ??
            parseBaseURL(legacyBaseURLValue) ??
            localURL
        let productionURL = parseBaseURL(processOrInfoValue(for: "FOUNDRY_API_BASE_URL_PRODUCTION")) ??
            parseBaseURL(legacyBaseURLValue) ??
            localURL

        let resolvedBaseURL: URL
        switch runtimeEnvironment {
        case .local:
            resolvedBaseURL = localURL
        case .staging:
            resolvedBaseURL = stagingURL
        case .production:
            resolvedBaseURL = productionURL
        }

        let apiVersion = processOrInfoValue(for: "FOUNDRY_API_VERSION") ?? defaultAPIVersion
        return AppEnvironment(runtimeEnvironment: runtimeEnvironment, baseURL: resolvedBaseURL, apiVersion: apiVersion)
    }

    private static func infoValue(for key: String) -> String? {
        guard let value = Bundle.main.object(forInfoDictionaryKey: key) as? String else {
            return nil
        }
        let trimmed = value.trimmingCharacters(in: .whitespacesAndNewlines)
        return trimmed.isEmpty ? nil : trimmed
    }

    private static func processOrInfoValue(for key: String) -> String? {
        if let value = ProcessInfo.processInfo.environment[key] {
            let trimmed = value.trimmingCharacters(in: .whitespacesAndNewlines)
            if !trimmed.isEmpty {
                return trimmed
            }
        }
        return infoValue(for: key)
    }

    private static func parseBaseURL(_ value: String?) -> URL? {
        guard let value else {
            return nil
        }

        let trimmed = value.trimmingCharacters(in: .whitespacesAndNewlines)
        let normalized = trimmed.trimmingCharacters(in: CharacterSet(charactersIn: "/"))
        guard !normalized.isEmpty else {
            return nil
        }

        return URL(string: normalized)
    }
}
