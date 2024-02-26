import {
  ContentLayout,
  Header,
  Cards,
  Container,
  SpaceBetween,
  Link,
  BreadcrumbGroup,
} from "@cloudscape-design/components";
import BaseAppLayout from "../../../components/base-app-layout";
import RouterButton from "../../../components/wrappers/router-button";
import useOnFollow from "../../../common/hooks/use-on-follow";
//import { CHATBOT_NAME } from "../../../common/constants";

export default function EcisoWelcome() {
  const onFollow = useOnFollow();

  return (
    <BaseAppLayout
      breadcrumbs={
        <BreadcrumbGroup
          onFollow={onFollow}
          items={[
            {
              text: "My eCISO",
              href: "/",
            },
          ]}
        />
      }
      content={
        <ContentLayout
          header={
            <Header
              variant="h1"
              description="An opensource solution utilizing AWS to help customers evaluate their cybersecurity infrastructure and implement necessary safeguards."
              actions={
                <RouterButton
                  iconAlign="right"
                  iconName="contact"
                  variant="primary"
                  href="/plugins/eciso"
                >
                  Start Evaluation
                </RouterButton>
              }
            >
              eCISO Home
            </Header>
          }
        >
          <SpaceBetween size="l">
            <Cards
              cardDefinition={{
                header: (item) => (
                  <Link
                    external={item.external}
                    href={item.href}
                    fontSize="heading-m"
                  >
                    {item.name}
                  </Link>
                ),
                sections: [
                  {
                    content: (item) => (
                      <div>
                        <img
                          src={item.img}
                          alt="Placeholder"
                          style={{ width: "100%" }}
                        />
                      </div>
                    ),
                  },
                  {
                    content: (item) => (
                      <div>
                        <div>{item.description}</div>
                      </div>
                    ),
                  },
                  {
                    id: "type",
                    header: "Type",
                    content: (item) => item.type,
                  },
                ],
              }}
              cardsPerRow={[{ cards: 1 }, { minWidth: 700, cards: 3 }]}
              items={[
                {
                  name: "CalPoly Digital Transformation Hub",
                  external: true,
                  type: "Innovation",
                  href: "https://aws.amazon.com/bedrock/",
                  img: "/images/plugins/eciso-dxhub.png",
                  description:
                    "An innovation engine solving real world challenges in the public sector.",
                },
                {
                  name: "eCISO Source Code",
                  external: true,
                  type: "Sourcecode",
                  href: "https://github.com/cal-poly-dxhub/aws-genai-llm-chatbot",
                  img: "/images/plugins/eciso-banner.png",
                  description:
                    "Browse our prototype implementation of eCISO utilizing the AWS Gen AI Chatbot framework..",
                },
                {
                  name: "AWS Gen AI Chatbot Framework",
                  type: "Framework",
                  href: "#",
                  img: "/images/welcome/ui-dark.png",
                  description:
                    "Fullstack framework to support rapid chatbot development on AWS.",
                },
              ]}
            />
            <Container
              media={{
                content: (
                  <img src="/images/plugins/image-placeholder.png" alt="placeholder" />
                ),
                width: 300,
                position: "side",
              }}
            >
              <Header
                variant="h1"
                description="The DxHub provides our partners with tangible solutions using innovative thinking and technology.                "
              >
                About the DxHub
              </Header>
              <p>
                The goal of the DxHub is to:
                <br/><br/>
                <ul>
                  <li>Provide students with real-world learning experiences</li>
                  <li>Apply proven innovation methodologies to challenging problems</li>
                  <li>Utilize the deep subject matter expertise of the public sector</li>
                  <li>Leverage the technology expertise of AWS and other partners</li>
                  <li>Solve challenging problems  in ways not contemplated before</li>
                </ul>
              </p>
              <Header
                variant="h1"
                description="The DxHub has a tremendous opportunity to make a positive impact here at Cal Poly as well as across the state, nation, and globe. Whether it’s helping law enforcement agencies to be more effective and efficient or addressing difficult challenges with non-profit organizations, we can make a difference with our innovation processes and technical depth in combination with public sector mission expertise. (Paul Jurasin, Founding Director)"
              >
                Our Process
              </Header>
              <p>
              The DxHub applies Amazon’s human-centered, ‘Working Backwards’ innovation methodology to tackle challenges facing government, education, and non-profit organizations.The DxHub team leads public sector organizations through innovation and solution workshops structured to generate big ideas and impactful solutions. Through product development sprints and customer validation testing, the team creates a ‘lean prototype’ that brings the solution to life. Students assist the team throughout the innovation process.
              </p>
            </Container>
           
           
          </SpaceBetween>
        </ContentLayout>
      }
    ></BaseAppLayout>
  );
}
