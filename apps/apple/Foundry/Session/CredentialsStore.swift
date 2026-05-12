import Foundation
import Security

final class CredentialsStore {
    static let shared = CredentialsStore(userDefaults: .standard, keychain: .default)

    private enum Key {
        static let accessTokenLegacy = "foundry.access_token"
        static let refreshTokenLegacy = "foundry.refresh_token"
        static let accessTokenAccount = "foundry.access_token"
        static let refreshTokenAccount = "foundry.refresh_token"
        static let currentUserEmail = "foundry.current_user_email"
        static let rememberedEmail = "foundry.remembered_email"
    }

    private let userDefaults: UserDefaults
    private let keychain: KeychainStore

    init(userDefaults: UserDefaults, keychain: KeychainStore = .default) {
        self.userDefaults = userDefaults
        self.keychain = keychain
    }

    func loadTokens() -> TokenPair? {
        guard
            let accessToken = keychain.read(account: Key.accessTokenAccount),
            let refreshToken = keychain.read(account: Key.refreshTokenAccount),
            !accessToken.isEmpty,
            !refreshToken.isEmpty
        else {
            return migrateLegacyTokensIfNeeded()
        }

        return TokenPair(accessToken: accessToken, refreshToken: refreshToken)
    }

    func loadCurrentUserEmail() -> String {
        userDefaults.string(forKey: Key.currentUserEmail) ?? ""
    }

    func saveSession(tokens: TokenPair, currentUserEmail: String) {
        keychain.save(tokens.accessToken, account: Key.accessTokenAccount)
        keychain.save(tokens.refreshToken, account: Key.refreshTokenAccount)
        userDefaults.set(currentUserEmail, forKey: Key.currentUserEmail)
        userDefaults.removeObject(forKey: Key.accessTokenLegacy)
        userDefaults.removeObject(forKey: Key.refreshTokenLegacy)
    }

    func clearSession() {
        keychain.delete(account: Key.accessTokenAccount)
        keychain.delete(account: Key.refreshTokenAccount)
        userDefaults.removeObject(forKey: Key.accessTokenLegacy)
        userDefaults.removeObject(forKey: Key.refreshTokenLegacy)
        userDefaults.removeObject(forKey: Key.currentUserEmail)
    }

    func loadRememberedEmail() -> String {
        userDefaults.string(forKey: Key.rememberedEmail) ?? ""
    }

    func rememberEmail(_ email: String) {
        userDefaults.set(email.trimmingCharacters(in: .whitespacesAndNewlines), forKey: Key.rememberedEmail)
    }

    func clearRememberedEmail() {
        userDefaults.removeObject(forKey: Key.rememberedEmail)
    }

    private func migrateLegacyTokensIfNeeded() -> TokenPair? {
        guard
            let accessToken = userDefaults.string(forKey: Key.accessTokenLegacy),
            let refreshToken = userDefaults.string(forKey: Key.refreshTokenLegacy),
            !accessToken.isEmpty,
            !refreshToken.isEmpty
        else {
            return nil
        }

        keychain.save(accessToken, account: Key.accessTokenAccount)
        keychain.save(refreshToken, account: Key.refreshTokenAccount)
        userDefaults.removeObject(forKey: Key.accessTokenLegacy)
        userDefaults.removeObject(forKey: Key.refreshTokenLegacy)

        return TokenPair(accessToken: accessToken, refreshToken: refreshToken)
    }
}

struct KeychainStore {
    static let `default` = KeychainStore(service: defaultService)

    let service: String

    func read(account: String) -> String? {
        var query = baseQuery(account: account)
        query[kSecReturnData as String] = true
        query[kSecMatchLimit as String] = kSecMatchLimitOne

        var result: CFTypeRef?
        let status = SecItemCopyMatching(query as CFDictionary, &result)
        guard status == errSecSuccess, let data = result as? Data else {
            return nil
        }

        return String(data: data, encoding: .utf8)
    }

    func save(_ value: String, account: String) {
        guard let data = value.data(using: .utf8) else {
            return
        }

        var query = baseQuery(account: account)
        let status = SecItemCopyMatching(query as CFDictionary, nil)

        if status == errSecSuccess {
            let attributesToUpdate = [kSecValueData as String: data]
            SecItemUpdate(query as CFDictionary, attributesToUpdate as CFDictionary)
            return
        }

        query[kSecValueData as String] = data
        SecItemAdd(query as CFDictionary, nil)
    }

    func delete(account: String) {
        let query = baseQuery(account: account)
        SecItemDelete(query as CFDictionary)
    }

    private func baseQuery(account: String) -> [String: Any] {
        [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: account
        ]
    }

    private static var defaultService: String {
        let bundleIdentifier = Bundle.main.bundleIdentifier ?? "technology.mcguire.foundry"
        return "\(bundleIdentifier).credentials"
    }
}
