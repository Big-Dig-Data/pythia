import Vue from "vue";
import Router from "vue-router";
import HomePage from "../pages/HomePage";
import PSHRecommendationsPage from "../pages/PSHRecommendationsPage";
import PublisherRecommendationsPage from "../pages/PublisherRecommendationsPage";
import AuthorRecommendationsPage from "../pages/AuthorRecommendationsPage";
import WorkDetailPage from "../pages/WorkDetailPage";
import NotFoundPage from "../pages/NotFoundPage";
import ExplicitTopicDetailPage from "../pages/ExplicitTopicDetailPage";
import CandidatesTablePage from "../pages/CandidatesTablePage";
import CandidateDetailPage from "../pages/CandidateDetailPage";
import SubjectTreePage from "../pages/SubjectTreePage";
import AcquisitionsPage from "../pages/AcquisitionsPage";
import { topicTypeToQueryParam } from "../libs/api";

Vue.use(Router);

let routes = [
  {
    path: "/",
    name: "home",
    component: HomePage,
  },
  {
    path: "/recommendations/psh",
    name: "psh recommendations",
    component: PSHRecommendationsPage,
  },
  {
    path: "/recommendations/publishers",
    name: "publisher recommendations",
    component: PublisherRecommendationsPage,
  },
  {
    path: "/recommendations/authors",
    name: "author recommendations",
    component: AuthorRecommendationsPage,
  },
  {
    path: "/work/detail",
    name: "work detail root",
    component: WorkDetailPage,
  },
  {
    path: "/work/detail/:workId",
    name: "work detail",
    component: WorkDetailPage,
    props: (route) => ({ workId: Number.parseInt(route.params.workId, 10) }),
  },
  {
    path: "/accept-invitation/",
    name: "accept-invitation",
    component: () => import("../pages/PasswordResetPage.vue"),
    meta: {
      outsideNormalLayout: true,
      invitation: true,
    },
  },
  {
    path: "/reset-password/",
    name: "reset-password",
    component: () => import("../pages/PasswordResetPage.vue"),
    meta: {
      outsideNormalLayout: true,
      invitation: false,
    },
  },
  {
    path: "/candidates",
    name: "candidates table",
    component: CandidatesTablePage,
    meta: {
      hideDateFilter: true,
      hideWorkFilter: true,
    },
  },
  {
    path: "/candidates/:candidateId",
    name: "candidate detail",
    component: CandidateDetailPage,
    props: (route) => ({
      candidateId: Number.parseInt(route.params.candidateId, 10),
    }),
    meta: {
      hideDateFilter: true,
      hideWorkFilter: true,
    },
  },
  {
    path: "/acquisitions",
    name: "acquisitions",
    component: AcquisitionsPage,
    meta: {
      hideDateFilter: true,
    },
  },
  // {
  //   // todo: PSH tree view is obsolete, but we might want to revive it later on
  //   path: "/psh-tree",
  //   name: "psh tree",
  //   component: PSHTreePage,
  //   obsolete: true,
  // },
  {
    path: "/user/",
    name: "user-page",
    component: () => import("../pages/UserPage.vue"),
  },
  {
    path: "*",
    component: NotFoundPage,
  },
];

for (let topicType of Object.keys(topicTypeToQueryParam)) {
  if (topicType != "psh") {
    routes.push({
      path: `/${topicType}/`,
      name: `${topicType} detail root`,
      component: ExplicitTopicDetailPage,
      props: () => ({ topicType }),
    });
  }
  routes.push({
    path: `/${topicType}/:topicId`,
    name: `${topicType} detail`,
    component: ExplicitTopicDetailPage,
    props: (route) => ({
      topicType,
      topicId: Number.parseInt(route.params.topicId, 10),
    }),
  });
}

export default new Router({
  routes: routes,
  mode: "history",
  linkActiveClass: "is-active",
});
