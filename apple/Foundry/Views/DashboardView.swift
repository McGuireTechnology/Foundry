import SwiftUI

struct DashboardView: View {
    @EnvironmentObject private var session: AppSession

    var body: some View {
        VStack(alignment: .leading, spacing: 28) {
            if !session.signedInEmail.isEmpty {
                Text("Welcome, \(session.signedInEmail)!")
                    .font(.system(size: 32, weight: .bold))
                    .foregroundStyle(VortexPalette.textPrimary)

                Text("Project Bootstrap Complete")
                    .font(.system(size: 28, weight: .bold))
                    .foregroundStyle(VortexPalette.textPrimary)
            } else {
                Text("Project Bootstrap Complete")
                    .font(.system(size: 32, weight: .bold))
                    .foregroundStyle(VortexPalette.textPrimary)
            }

            Text("This workspace now includes API, web builder, and docs scaffolding.")
                .font(.system(size: 16, weight: .regular))
                .foregroundStyle(VortexPalette.textPrimary)

            VStack(alignment: .leading, spacing: 10) {
                BulletLine(text: "Define data models")
                BulletLine(text: "Build page schema and renderer")
                BulletLine(text: "Add workflow/actions engine")
            }
        }
        .padding(.horizontal, 36)
        .padding(.vertical, 32)
        .frame(maxWidth: .infinity, alignment: .leading)
        .vortexPanelStyle()
    }
}

private struct BulletLine: View {
    let text: String

    var body: some View {
        HStack(alignment: .firstTextBaseline, spacing: 16) {
            Text("•")
                .font(.system(size: 20, weight: .regular))
                .foregroundStyle(VortexPalette.textPrimary)
            Text(text)
                .font(.system(size: 16, weight: .regular))
                .foregroundStyle(VortexPalette.textPrimary)
        }
    }
}
