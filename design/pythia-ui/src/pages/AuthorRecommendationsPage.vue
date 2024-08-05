<i18n>
en:
  main_title: Recommended authors

cs:
  main_title: Doporučení autoři
</i18n>

<template>
  <v-container fluid>
    <v-row>
      <v-col>
        <h2>{{ $t("main_title") }}</h2>
      </v-col>
    </v-row>
    <v-row>
      <v-col class="py-0">
        <ExplicitTopicRecommendationsWidget topic-type="author" />
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import ExplicitTopicRecommendationsWidget from "../components/ExplicitTopicRecommendationsWidget";

export default {
  name: "AuthorRecommendationsPage",
  components: { ExplicitTopicRecommendationsWidget },
};
</script>
