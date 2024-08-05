<i18n>
en:
  main_title: Publisher recommendations

cs:
  main_title: Doporučení vydavatelé
</i18n>

<template>
  <v-container fluid>
    <v-row>
      <v-col>
        <h2 class="section-header">{{ $t("main_title") }}</h2>
      </v-col>
    </v-row>
    <v-row>
      <v-col class="py-0">
        <ExplicitTopicRecommendationsWidget topic-type="publisher" />
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import ExplicitTopicRecommendationsWidget from "../components/ExplicitTopicRecommendationsWidget";

export default {
  name: "PublisherRecommendationsPage",
  components: { ExplicitTopicRecommendationsWidget },
};
</script>
