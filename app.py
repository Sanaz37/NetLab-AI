
import random

import streamlit as st


st.set_page_config(
    page_title="NetLab AI",
    page_icon="🌐",
    layout="wide",
)


SCENARIOS = [
    {
        "id": "bgp-101",
        "level": "Beginner",
        "title": "BGP Neighbor Is Not Established",
        "topology": "R1 (AS 65001) ---- R2 (AS 65002)",
        "prompt": (
            "The BGP session between two routers is not established. "
            "Investigate the neighbor state, identify the root cause, "
            "and propose a fix."
        ),
        "commands": {
            "show ip bgp summary": """
Neighbor       V   AS      MsgRcvd MsgSent Up/Down  State/PfxRcd
192.0.2.2      4   65020   0       0       never    Active
""",
            "show running-config | section router bgp": """
router bgp 65001
 neighbor 192.0.2.2 remote-as 65020
""",
            "show ip route": """
Gateway of last resort is not set.
Connected routes are available.
""",
        },
        "diagnosis_keywords": [
            "remote-as",
            "remote as",
            "as mismatch",
            "incorrect as",
            "wrong as",
            "65020",
            "65002",
        ],
        "evidence_keywords": [
            "show ip bgp summary",
            "active",
            "65020",
            "show running-config",
        ],
        "fix_keywords": [
            "remote-as 65002",
            "correct remote-as",
            "fix the as",
            "65002",
        ],
        "verify_keywords": [
            "established",
            "show ip bgp summary",
        ],
        "explanation": (
            "The configured remote AS on R1 does not match the actual "
            "AS of R2. R1 is configured with remote-as 65020, while "
            "R2 uses AS 65002."
        ),
        "solution": (
            "Configure the correct neighbor AS on R1: "
            "neighbor 192.0.2.2 remote-as 65002. "
            "Then verify the session using show ip bgp summary."
        ),
    },
    {
        "id": "bgp-102",
        "level": "Beginner",
        "title": "A BGP Network Is Not Advertised",
        "topology": "R1 (AS 65001) ---- R2 (AS 65002)",
        "prompt": (
            "The BGP session is established, but prefix 10.30.0.0/24 "
            "is not being advertised to the neighbor. Find the cause."
        ),
        "commands": {
            "show ip bgp summary": """
Neighbor       V   AS      Up/Down    State/PfxRcd
192.0.2.2      4   65002   01:15:20   12
""",
            "show running-config | section router bgp": """
router bgp 65001
 network 10.30.0.0 mask 255.255.0.0
 neighbor 192.0.2.2 remote-as 65002
""",
            "show ip route 10.30.0.0": """
Routing entry for 10.30.0.0/24
Known via "connected"
""",
        },
        "diagnosis_keywords": [
            "mask",
            "subnet mask",
            "network statement",
            "prefix length",
            "255.255.0.0",
            "mismatch",
        ],
        "evidence_keywords": [
            "show ip route",
            "255.255.0.0",
            "10.30.0.0/24",
            "network 10.30.0.0",
        ],
        "fix_keywords": [
            "255.255.255.0",
            "correct the mask",
            "fix the mask",
            "correct the network statement",
        ],
        "verify_keywords": [
            "show ip bgp",
            "show ip bgp summary",
            "10.30.0.0/24",
        ],
        "explanation": (
            "The BGP network statement uses a /16 mask, but the actual "
            "route in the routing table is a /24. In this scenario, "
            "the network statement must match the route exactly."
        ),
        "solution": (
            "Correct the network statement to use the actual subnet "
            "mask: network 10.30.0.0 mask 255.255.255.0. "
            "Then verify the prefix in the BGP table and on the neighbor."
        ),
    },
    {
        "id": "bgp-201",
        "level": "Intermediate",
        "title": "An Inbound Policy Blocks a Prefix",
        "topology": "R1 (AS 65001) ---- R2 (AS 65002)",
        "prompt": (
            "The BGP session is established and other prefixes are "
            "received, but 10.20.0.0/24 is missing. Investigate why."
        ),
        "commands": {
            "show ip bgp summary": """
Neighbor       V   AS      Up/Down    State/PfxRcd
192.0.2.2      4   65002   02:30:10   12
""",
            "show ip prefix-list BLOCKED": """
ip prefix-list BLOCKED: 2 entries
 seq 5 deny 10.20.0.0/24
 seq 10 permit 0.0.0.0/0 le 32
""",
            "show route-map IN-FROM-R2": """
route-map IN-FROM-R2 permit 10
 match ip address prefix-list BLOCKED
""",
        },
        "diagnosis_keywords": [
            "prefix-list",
            "prefix list",
            "route-map",
            "route map",
            "filter",
            "filtering",
            "deny",
            "blocked",
        ],
        "evidence_keywords": [
            "show ip prefix-list",
            "deny 10.20.0.0/24",
            "route-map",
            "prefix-list blocked",
        ],
        "fix_keywords": [
            "correct the prefix-list",
            "fix the prefix-list",
            "correct the filter",
            "remove the deny",
            "permit 10.20.0.0/24",
            "correct the route-map",
        ],
        "verify_keywords": [
            "show ip bgp",
            "show ip route",
            "10.20.0.0/24",
        ],
        "explanation": (
            "The prefix list denies 10.20.0.0/24. It is referenced by "
            "the inbound route map. Because the matching route-map "
            "sequence does not match a denied prefix-list entry, the "
            "route may be rejected by the route map's implicit deny."
        ),
        "solution": (
            "Correct the prefix list or route map according to the "
            "intended routing policy. Verify that the target prefix "
            "is permitted and that other filtering requirements remain "
            "enforced."
        ),
    },
    {
        "id": "bgp-202",
        "level": "Intermediate",
        "title": "BGP Next Hop Is Unreachable",
        "topology": "R1 ---- R2 (iBGP) ---- R3",
        "prompt": (
            "Prefix 10.40.0.0/24 is present in BGP, but it is not "
            "selected as a usable route. Investigate the next hop."
        ),
        "commands": {
            "show ip bgp 10.40.0.0/24": """
Paths: (1 available, no best path)
  65002
    10.0.12.2 (inaccessible) from 192.0.2.2
""",
            "show ip route 10.0.12.2": """
% Network not in table
""",
            "show running-config | section router bgp": """
router bgp 65001
 neighbor 192.0.2.2 remote-as 65001
""",
        },
        "diagnosis_keywords": [
            "next-hop",
            "next hop",
            "unreachable next hop",
            "next-hop reachability",
            "inaccessible",
        ],
        "evidence_keywords": [
            "inaccessible",
            "show ip route 10.0.12.2",
            "no best path",
            "next-hop",
        ],
        "fix_keywords": [
            "next-hop-self",
            "static route",
            "ip route",
            "add a route",
            "make the next hop reachable",
            "next-hop reachability",
        ],
        "verify_keywords": [
            "show ip bgp",
            "show ip route",
            "best path",
            "reachable",
        ],
        "explanation": (
            "The next hop 10.0.12.2 is unreachable. The router cannot "
            "use this BGP path until it has IP reachability to the "
            "next-hop address."
        ),
        "solution": (
            "Restore reachability to the next hop. Depending on the "
            "topology, this may require an appropriate route or the "
            "next-hop-self setting on the relevant BGP neighbor. "
            "Verify next-hop reachability and route selection afterward."
        ),
    },
    {
        "id": "bgp-301",
        "level": "Advanced",
        "title": "Incorrect Route Selection Due to Local Preference",
        "topology": "R1 receives two paths through R2 and R3",
        "prompt": (
            "Two BGP paths exist for 10.50.0.0/24. Network policy "
            "requires the path through R2, but R1 selects the path "
            "through R3. Diagnose the problem."
        ),
        "commands": {
            "show ip bgp 10.50.0.0/24": """
BGP routing table entry for 10.50.0.0/24
Paths: (2 available, best #2)
  65002
    192.0.2.2, localpref 50
  65003
    192.0.2.3, localpref 100, best
""",
            "show route-map PREFER-R2": """
route-map PREFER-R2 permit 10
 set local-preference 50
""",
            "show ip bgp summary": """
Neighbor       V   AS      Up/Down    State/PfxRcd
192.0.2.2      4   65002   03:20:10   20
192.0.2.3      4   65003   03:18:04   25
""",
        },
        "diagnosis_keywords": [
            "local-preference",
            "local preference",
            "localpref",
            "local pref",
        ],
        "evidence_keywords": [
            "localpref 50",
            "localpref 100",
            "show ip bgp 10.50.0.0/24",
            "route-map",
        ],
        "fix_keywords": [
            "local-preference 200",
            "increase local preference",
            "set local preference",
            "correct the route-map",
            "change local-preference",
        ],
        "verify_keywords": [
            "show ip bgp 10.50.0.0/24",
            "best path",
            "verify route selection",
            "path through r2",
        ],
        "explanation": (
            "The path through R2 has local preference 50, while the "
            "path through R3 has local preference 100. Assuming earlier "
            "selection criteria do not override this comparison, BGP "
            "prefers the path with the higher local preference."
        ),
        "solution": (
            "Adjust the local-preference policy so the path through R2 "
            "receives a higher value than the alternative path. Then "
            "verify the selected best path in the BGP table."
        ),
    },
    {
        "id": "bgp-302",
        "level": "Advanced",
        "title": "An AS_PATH Filter Rejects a Prefix",
        "topology": "R1 (AS 65001) ---- R2 (AS 65002) ---- AS 65100",
        "prompt": (
            "The BGP session is established, but prefix 10.60.0.0/24 "
            "is not present in the local BGP table. Investigate the "
            "AS_PATH filtering policy."
        ),
        "commands": {
            "show ip bgp 10.60.0.0/24": """
% Network not in table
""",
            "show running-config | include as-path|filter-list": """
ip as-path access-list 10 permit ^65002$
 neighbor 192.0.2.2 filter-list 10 in
""",
            "show ip bgp summary": """
Neighbor       V   AS      Up/Down    State/PfxRcd
192.0.2.2      4   65002   01:42:15   18
""",
        },
        "diagnosis_keywords": [
            "as-path",
            "as path",
            "filter-list",
            "filter list",
            "regular expression",
            "regex",
        ],
        "evidence_keywords": [
            "as-path access-list",
            "filter-list",
            "show ip bgp 10.60.0.0/24",
            "65002",
        ],
        "fix_keywords": [
            "correct the filter",
            "fix the regex",
            "correct the regex",
            "modify the as-path access-list",
            "update the filter-list",
            "permit the intended path",
        ],
        "verify_keywords": [
            "show ip bgp",
            "10.60.0.0/24",
            "show ip bgp summary",
        ],
        "explanation": (
            "The expression ^65002$ matches an AS_PATH containing "
            "exactly AS 65002. A path that also contains AS 65100 "
            "does not match that expression and may therefore be "
            "filtered by the inbound policy."
        ),
        "solution": (
            "Adjust the AS_PATH access list to match the intended "
            "routing policy. Avoid removing filtering indiscriminately. "
            "Verify that permitted prefixes are accepted and unwanted "
            "paths remain filtered."
        ),
    },
]


def contains_any(text, keywords):
    normalized_text = text.lower().replace("-", " ")
    normalized_keywords = [
        keyword.lower().replace("-", " ")
        for keyword in keywords
    ]
    return any(
        keyword in normalized_text
        for keyword in normalized_keywords
    )


def evaluate_answer(
    scenario,
    diagnosis,
    evidence,
    fix,
    verification,
):
    scores = {
        "Root cause identification": (
            40
            if contains_any(
                diagnosis,
                scenario["diagnosis_keywords"],
            )
            else 0
        ),
        "Technical evidence": (
            25
            if len(evidence.strip()) >= 15
            and contains_any(
                evidence,
                scenario["evidence_keywords"],
            )
            else 0
        ),
        "Corrective action": (
            25
            if contains_any(
                fix,
                scenario["fix_keywords"],
            )
            else 0
        ),
        "Verification plan": (
            10
            if contains_any(
                verification,
                scenario["verify_keywords"],
            )
            else 0
        ),
    }
    return scores


st.title("🌐 NetLab AI")
st.subheader("AI-Powered Network Troubleshooting Simulator")

st.write(
    "Practice network troubleshooting through interactive "
    "BGP scenarios inspired by CCNP-level topics."
)

st.info(
    "Prototype version 0.1: Scenarios are predefined and selected "
    "randomly. The application is not connected to an AI API yet. "
    "Scoring uses keyword matching and is not a complete assessment "
    "of technical correctness."
)

level = st.selectbox(
    "Choose difficulty level",
    ["Beginner", "Intermediate", "Advanced"],
)

if st.button("🎲 Generate Random Scenario", type="primary"):
    available_scenarios = [
        scenario
        for scenario in SCENARIOS
        if scenario["level"] == level
    ]

    st.session_state["scenario"] = random.choice(
        available_scenarios
    )

    for key in (
        "last_output",
        "last_command",
        "evaluation",
    ):
        st.session_state.pop(key, None)

scenario = st.session_state.get("scenario")

if scenario:
    st.divider()
    st.header(scenario["title"])
    st.caption(f"Difficulty: {scenario['level']}")

    st.markdown(f"**Topology:** `{scenario['topology']}`")
    st.write(scenario["prompt"])

    st.subheader("1. Troubleshooting Console")

    command = st.selectbox(
        "Select a command to inspect",
        list(scenario["commands"].keys()),
        key=f"command_{scenario['id']}",
    )

    if st.button("▶️ Run Command"):
        st.session_state["last_command"] = command
        st.session_state["last_output"] = (
            scenario["commands"][command]
        )

    if st.session_state.get("last_output"):
        st.caption(
            "Command: "
            + st.session_state.get("last_command", "")
        )
        st.code(
            st.session_state["last_output"],
            language="text",
        )

    st.subheader("2. Submit Your Troubleshooting Report")

    st.write(
        "Identify the root cause, cite evidence from command output, "
        "recommend a fix, and explain how you would verify the result."
    )

    with st.form(key=f"answer_{scenario['id']}"):
        diagnosis = st.text_area(
            "A. What is the root cause?",
            placeholder="Explain the technical cause...",
        )

        evidence = st.text_area(
            "B. What evidence supports your diagnosis?",
            placeholder="Reference commands and relevant output...",
        )

        fix = st.text_area(
            "C. What corrective action would you take?",
            placeholder="Describe the configuration change or fix...",
        )

        verification = st.text_area(
            "D. How would you verify that the issue is resolved?",
            placeholder="List verification commands and expected results...",
        )

        submitted = st.form_submit_button("Evaluate My Answer")

    if submitted:
        score_details = evaluate_answer(
            scenario,
            diagnosis,
            evidence,
            fix,
            verification,
        )

        st.session_state["evaluation"] = {
            "scenario_id": scenario["id"],
            "details": score_details,
            "score": sum(score_details.values()),
        }

    evaluation = st.session_state.get("evaluation")

    if (
        evaluation
        and evaluation["scenario_id"] == scenario["id"]
    ):
        st.divider()
        st.header("3. Assessment Results")

        st.metric(
            "Prototype Score",
            f"{evaluation['score']} / 100",
        )

        for category, points in evaluation["details"].items():
            st.write(f"**{category}:** {points} points")

        if evaluation["score"] >= 80:
            st.success(
                "Good start. Compare your reasoning with the reference solution."
            )
        elif evaluation["score"] >= 50:
            st.warning(
                "Some parts of your answer matched the expected response. "
                "Review the evidence and proposed fix."
            )
        else:
            st.error(
                "This scenario needs more investigation. Review the "
                "command output and try to refine your diagnosis."
            )

        with st.expander("Show Reference Explanation and Solution"):
            st.markdown("**Expected Root Cause**")
            st.write(scenario["explanation"])

            st.markdown("**Suggested Solution**")
            st.write(scenario["solution"])

else:
    st.warning(
        "Choose a difficulty level and click "
        "'Generate Random Scenario' to begin."
    )

st.divider()
st.caption(
    "NetLab AI | Educational Prototype | Version 0.1"
)
